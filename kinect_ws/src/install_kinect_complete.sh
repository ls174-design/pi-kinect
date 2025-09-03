#!/bin/bash
echo "========================================"
echo "  Complete Kinect Driver Installation"
echo "========================================"
echo "This script will install all necessary dependencies"
echo "and build libfreenect from source for Ubuntu 18.04"
echo ""

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo "❌ Please don't run this script as root (sudo)"
    echo "The script will use sudo for individual commands when needed"
    exit 1
fi

# Update package list
echo "Step 1: Updating package list..."
sudo apt-get update -y

# Install all build dependencies
echo "Step 2: Installing build dependencies..."
sudo apt-get install -y \
    build-essential \
    cmake \
    pkg-config \
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
    swig \
    cython3 \
    git \
    wget \
    curl

# Install additional Python packages
echo "Step 3: Installing Python packages..."
pip3 install --user numpy cython

# Create temporary directory
TEMP_DIR="/tmp/kinect_install_$$"
mkdir -p "$TEMP_DIR"
cd "$TEMP_DIR"

# Download libfreenect
echo "Step 4: Downloading libfreenect source..."
wget -O libfreenect.tar.gz https://github.com/OpenKinect/libfreenect/archive/v0.5.7.tar.gz
tar -xzf libfreenect.tar.gz
cd libfreenect-0.5.7

# Build libfreenect
echo "Step 5: Building libfreenect..."
mkdir build
cd build

# Configure with Python 3 support
cmake .. \
    -DBUILD_PYTHON3=ON \
    -DPYTHON3_EXECUTABLE=/usr/bin/python3 \
    -DPYTHON3_INCLUDE_DIR=/usr/include/python3.6 \
    -DPYTHON3_LIBRARY=/usr/lib/arm-linux-gnueabh/libpython3.6m.so \
    -DCMAKE_INSTALL_PREFIX=/usr/local

# Build
make -j$(nproc)

# Install
echo "Step 6: Installing libfreenect..."
sudo make install

# Update library cache
sudo ldconfig

# Clean up
cd /
rm -rf "$TEMP_DIR"

# Test installation
echo "Step 7: Testing installation..."
if python3 -c "import freenect; print('✅ freenect library installed successfully')" 2>/dev/null; then
    echo "✅ freenect library installed successfully!"
else
    echo "⚠️  freenect library not found, trying alternative installation..."
    
    # Try installing via pip as fallback
    echo "Trying pip installation as fallback..."
    pip3 install --user freenect-py
    
    # Test again
    if python3 -c "import freenect; print('✅ freenect library installed successfully')" 2>/dev/null; then
        echo "✅ freenect library installed via pip!"
    else
        echo "❌ freenect library installation failed"
        echo "You may need to install it manually or use the test streamer"
    fi
fi

# Check for Kinect device
echo "Step 8: Checking for Kinect device..."
if lsusb | grep -i "microsoft\|kinect\|xbox" > /dev/null; then
    echo "✅ Kinect device detected:"
    lsusb | grep -i "microsoft\|kinect\|xbox"
else
    echo "⚠️  No Kinect device detected. Make sure it's connected via USB."
fi

echo ""
echo "========================================"
echo "  Kinect Installation Complete!"
echo "========================================"
echo "You can now try running:"
echo "  python3 ~/kinect_ws/kinect_streamer.py"
echo ""
echo "If the installation failed, you can still use:"
echo "  python3 ~/kinect_ws/test_streamer.py"
echo "========================================"
