#!/bin/bash
set -euo pipefail

echo "🔧 Pi-Kinect Raspberry Pi Setup"
echo "================================"

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
    python3-pip \
    python3-dev \
    python3-opencv \
    python3-numpy \
    python3-pil \
    python3-tk \
    cmake \
    libusb-1.0-0-dev \
    libxmu-dev \
    libxi-dev \
    libgl1-mesa-dev \
    libglu1-mesa-dev \
    libxrandr-dev \
    libxinerama-dev \
    libxcursor-dev \
    swig \
    build-essential

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

# Install Pi-Kinect
echo "🐍 Installing Pi-Kinect..."
pip3 install --upgrade pip
pip3 install pi-kinect

# Create udev rules for non-root access
echo "🔧 Setting up udev rules for non-root access..."
sudo tee /etc/udev/rules.d/51-kinect.rules > /dev/null << 'EOF'
# Kinect v1 udev rules
SUBSYSTEM=="usb", ATTR{idVendor}=="045e", ATTR{idProduct}=="02b0", MODE="0666"
SUBSYSTEM=="usb", ATTR{idVendor}=="045e", ATTR{idProduct}=="02ad", MODE="0666"
SUBSYSTEM=="usb", ATTR{idVendor}=="045e", ATTR{idProduct}=="02ae", MODE="0666"
SUBSYSTEM=="usb", ATTR{idVendor}=="045e", ATTR{idProduct}=="02c2", MODE="0666"
SUBSYSTEM=="usb", ATTR{idVendor}=="045e", ATTR{idProduct}=="02be", MODE="0666"
SUBSYSTEM=="usb", ATTR{idVendor}=="045e", ATTR{idProduct}=="02bf", MODE="0666"
EOF

# Reload udev rules
echo "🔄 Reloading udev rules..."
sudo udevadm control --reload-rules
sudo udevadm trigger

# Add user to required groups
echo "👤 Adding user to required groups..."
sudo adduser $USER video
sudo adduser $USER plugdev

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

try:
    import pi_kinect
    print('✅ Pi-Kinect package imported successfully')
    print('✅ Pi-Kinect version:', pi_kinect.__version__)
except ImportError as e:
    print('❌ Pi-Kinect import failed:', e)
"

echo ""
echo "🎯 Installation complete!"
echo ""
echo "Next steps:"
echo "1. Reboot your Pi or log out/in to apply group changes"
echo "2. Connect your Kinect"
echo "3. Test with: pi-kinect probe"
echo "4. Start streaming with: pi-kinect stream"
echo "5. Open http://YOUR_PI_IP:8080 in your browser"
echo ""
echo "If you see any errors above, please check the installation logs."
