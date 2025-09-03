#!/bin/bash
set -euo pipefail

echo "🔧 Setting up Pi-Kinect on Raspberry Pi"
echo "======================================="

# Install system dependencies
echo "📦 Installing system dependencies..."
sudo apt-get update
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
    build-essential \
    libfreenect-dev \
    libfreenect0.5

# Build freenect Python bindings
echo "🔨 Building freenect Python bindings..."
if [ ! -d "libfreenect" ]; then
    git clone https://github.com/OpenKinect/libfreenect.git
fi
cd libfreenect/wrappers/python
sudo python3 setup.py install
cd ~

# Add user to required groups
echo "👤 Adding user to required groups..."
sudo adduser $USER video
sudo adduser $USER plugdev

# Install Pi-Kinect
echo "🐍 Installing Pi-Kinect..."
if [ -d "pi_kinect" ]; then
    cd pi_kinect
    pip3 install -e .
    cd ~
else
    echo "❌ pi_kinect directory not found. Please copy it from Windows first:"
    echo "   scp -r pi_kinect ls@192.168.1.9:~/"
    exit 1
fi

# Test installation
echo "🧪 Testing installation..."
python3 -c "
try:
    import freenect
    print('✅ freenect imported successfully')
    
    # Test freenect functionality
    ctx = freenect.init()
    if ctx:
        num_devices = freenect.num_devices(ctx)
        print(f'✅ Freenect devices found: {num_devices}')
        freenect.shutdown(ctx)
    else:
        print('⚠️ Freenect context initialization failed')
        
except ImportError as e:
    print('❌ Freenect import failed:', e)
except Exception as e:
    print('⚠️ Freenect test failed:', e)
"

echo ""
echo "🎯 Setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Test with: pi-kinect probe --verbose"
echo "2. Start streaming with: pi-kinect stream --host 0.0.0.0 --port 8080"
echo "3. Open http://192.168.1.9:8080 in your browser"
echo ""
echo "🔍 To test Kinect detection:"
echo "pi-kinect probe --verbose"
