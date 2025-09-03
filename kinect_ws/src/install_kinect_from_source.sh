#!/bin/bash
echo "Installing Kinect support from source on Ubuntu 18.04..."

# Update package list
echo "Updating package list..."
sudo apt-get update

# Install build dependencies
echo "Installing build dependencies..."
sudo apt-get install -y \
    cmake \
    libusb-1.0-0-dev \
    libxmu-dev \
    libxi-dev \
    libgl1-mesa-dev \
    libglu1-mesa-dev \
    libxrandr-dev \
    libxinerama-dev \
    libxcursor-dev \
    libxi-dev \
    python3-dev \
    python3-numpy \
    swig

# Download and build libfreenect
echo "Downloading libfreenect..."
cd /tmp
wget https://github.com/OpenKinect/libfreenect/archive/v0.5.7.tar.gz
tar -xzf v0.5.7.tar.gz
cd libfreenect-0.5.7

# Build libfreenect
echo "Building libfreenect..."
mkdir build
cd build
cmake .. -DBUILD_PYTHON3=ON
make -j4
sudo make install

# Update library cache
sudo ldconfig

# Verify installation
echo "Verifying installation..."
python3 -c "import freenect; print('✅ freenect library installed successfully')"

echo "Kinect support installation complete!"
echo "You can now run: python3 kinect_streamer.py"
