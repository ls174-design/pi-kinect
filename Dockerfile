# Pi-Kinect Docker Image
FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libusb-1.0-0-dev \
    cmake \
    build-essential \
    libxmu-dev \
    libxi-dev \
    libgl1-mesa-dev \
    libglu1-mesa-dev \
    libxrandr-dev \
    libxinerama-dev \
    libxcursor-dev \
    libfreenect-dev \
    libfreenect0.5 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY pi_kinect/requirements.txt pi_kinect/constraints.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt -c constraints.txt

# Copy the application
COPY pi_kinect/ ./pi_kinect/

# Install the package
RUN pip install --no-cache-dir -e ./pi_kinect/

# Create non-root user
RUN useradd -m -s /bin/bash pi-kinect && \
    usermod -a -G video,plugdev pi-kinect

# Switch to non-root user
USER pi-kinect

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/status || exit 1

# Default command
CMD ["pi-kinect", "stream", "--host", "0.0.0.0", "--port", "8080"]
