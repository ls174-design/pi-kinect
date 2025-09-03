#!/bin/bash
echo "🔧 Installing freenect from source (following GitHub gist method)"
echo "================================================================="

# Check if freenect is already working
echo "🔍 Checking if freenect is already available..."
if python3 -c "import freenect" 2>/dev/null; then
    echo "✅ freenect is already available!"
    exit 0
fi

# Update system first
echo "📦 Updating system packages..."
sudo apt-get update
sudo apt-get upgrade -y

# Install dependencies (following the gist exactly)
echo "📦 Installing build dependencies..."
sudo apt-get install -y \
    git-core \
    cmake \
    freeglut3-dev \
    pkg-config \
    build-essential \
    libxmu-dev \
    libxi-dev \
    libusb-1.0-0-dev \
    cython \
    python3-dev \
    python3-numpy

# Create temporary directory
TEMP_DIR=$(mktemp -d)
cd "$TEMP_DIR"

echo "📥 Downloading libfreenect source..."
git clone git://github.com/OpenKinect/libfreenect.git
cd libfreenect

echo "🔨 Building libfreenect..."
mkdir build
cd build

# Configure (following gist method)
cmake -L ..
make

# Install
echo "📦 Installing libfreenect..."
sudo make install

# Update library cache (following gist)
echo "🔄 Updating library cache..."
sudo ldconfig /usr/local/lib64/

# Add user to video and plugdev groups (following gist)
echo "👤 Adding user to required groups..."
sudo adduser $USER video
sudo adduser $USER plugdev

# Create udev rules for non-root access (following gist)
echo "🔧 Setting up udev rules for non-root access..."
sudo tee /etc/udev/rules.d/51-kinect.rules > /dev/null << 'EOF'
# ATTR{product}=="Xbox NUI Motor"
SUBSYSTEM=="usb", ATTR{idVendor}=="045e", ATTR{idProduct}=="02b0", MODE="0666"
# ATTR{product}=="Xbox NUI Audio"
SUBSYSTEM=="usb", ATTR{idVendor}=="045e", ATTR{idProduct}=="02ad", MODE="0666"
# ATTR{product}=="Xbox NUI Camera"
SUBSYSTEM=="usb", ATTR{idVendor}=="045e", ATTR{idProduct}=="02ae", MODE="0666"
# ATTR{product}=="Xbox NUI Motor"
SUBSYSTEM=="usb", ATTR{idVendor}=="045e", ATTR{idProduct}=="02c2", MODE="0666"
# ATTR{product}=="Xbox NUI Motor"
SUBSYSTEM=="usb", ATTR{idVendor}=="045e", ATTR{idProduct}=="02be", MODE="0666"
# ATTR{product}=="Xbox NUI Motor"
SUBSYSTEM=="usb", ATTR{idVendor}=="045e", ATTR{idProduct}=="02bf", MODE="0666"
EOF

# Install Python bindings (following gist method)
echo "🐍 Installing Python bindings..."
cd ../wrappers/python
sudo python3 setup.py install

# Reload udev rules
echo "🔄 Reloading udev rules..."
sudo udevadm control --reload-rules
sudo udevadm trigger

# Test installation
echo "🧪 Testing installation..."
if python3 -c "import freenect; print('✅ freenect Python bindings installed successfully')" 2>/dev/null; then
    echo "✅ freenect installation successful!"
    
    # Test freenect-glview if available
    if command -v freenect-glview &> /dev/null; then
        echo "✅ freenect-glview is available for testing"
        echo "💡 You can test with: freenect-glview"
    fi
else
    echo "❌ freenect Python bindings installation failed"
    echo "🔍 Checking for common issues..."
    
    # Check if libfreenect was installed
    if [ -f "/usr/local/lib/libfreenect.so" ] || [ -f "/usr/lib/libfreenect.so" ]; then
        echo "✅ libfreenect library found"
    else
        echo "❌ libfreenect library not found"
    fi
    
    # Check Python path
    echo "🔍 Python path:"
    python3 -c "import sys; print('\n'.join(sys.path))"
fi

# Cleanup
cd /
rm -rf "$TEMP_DIR"

echo ""
echo "🎯 freenect installation complete!"
echo ""
echo "📋 Next steps:"
echo "1. Reboot your Pi or log out/in to apply group changes"
echo "2. Connect your Kinect"
echo "3. Test with: freenect-glview"
echo "4. Test Python with: python3 -c 'import freenect; print(freenect.num_devices(freenect.init()))'"
