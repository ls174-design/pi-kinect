#!/bin/bash
echo "🔧 Raspberry Pi Library Setup"
echo "============================="

# Check if we're running as root
if [ "$EUID" -eq 0 ]; then
    echo "⚠️  Running as root. Consider using a regular user account."
fi

# Update package list
echo "📦 Updating package list..."
sudo apt-get update

# Install system dependencies
echo "📦 Installing system dependencies..."
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
    python3-dev \
    python3-numpy \
    swig \
    build-essential

# Install OpenCV system libraries
echo "📦 Installing OpenCV system libraries..."
sudo apt-get install -y \
    libopencv-dev \
    python3-opencv \
    libopencv-contrib-dev

# Install freenect system libraries
echo "📦 Installing freenect system libraries..."
sudo apt-get install -y \
    libfreenect-dev \
    libfreenect0.5

# Try to install python3-freenect, but don't fail if not available
echo "📦 Attempting to install python3-freenect..."
if sudo apt-get install -y python3-freenect 2>/dev/null; then
    echo "✅ python3-freenect installed from package"
else
    echo "⚠️ python3-freenect not available in repositories, will install via pip"
fi

# Install Python package manager
echo "📦 Installing Python package manager..."
sudo apt-get install -y python3-pip

# Install Python packages
echo "🐍 Installing Python packages..."
pip3 install --upgrade pip

# Install NumPy from system package first (pre-compiled)
echo "📦 Installing NumPy from system package (pre-compiled)..."
sudo apt-get install -y python3-numpy

# Install other packages
echo "📦 Installing other Python packages..."
pip3 install \
    opencv-python \
    pillow \
    requests \
    freenect

# Update library cache
echo "🔄 Updating library cache..."
sudo ldconfig

# Verify installation
echo "✅ Verifying installation..."
echo "Testing Python imports..."

python3 -c "
import sys
print('Python version:', sys.version)

try:
    import cv2
    print('✅ OpenCV version:', cv2.__version__)
except ImportError as e:
    print('❌ OpenCV import failed:', e)

try:
    import numpy as np
    print('✅ NumPy version:', np.__version__)
except ImportError as e:
    print('❌ NumPy import failed:', e)

try:
    import freenect
    print('✅ Freenect imported successfully')
    
    # Test freenect functionality
    ctx = freenect.init()
    if ctx:
        num_devices = freenect.num_devices(ctx)
        print('✅ Freenect devices found:', num_devices)
        freenect.shutdown(ctx)
    else:
        print('⚠️ Freenect context initialization failed')
        
except ImportError as e:
    print('❌ Freenect import failed:', e)
except Exception as e:
    print('⚠️ Freenect test failed:', e)
"

echo ""
echo "🎯 Installation complete!"
echo ""
echo "Next steps:"
echo "1. Connect your Kinect to the Pi"
echo "2. Run: python3 kinect_unified_streamer.py"
echo "3. Open http://YOUR_PI_IP:8080 in your browser"
echo ""
echo "If you see any errors above, please check the installation logs."
