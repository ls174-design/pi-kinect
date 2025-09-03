#!/bin/bash
echo "🔧 Complete Raspberry Pi Kinect Setup"
echo "====================================="

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to test freenect
test_freenect() {
    python3 -c "import freenect; print('✅ freenect working')" 2>/dev/null
}

# Update package list
echo "📦 Updating package list..."
sudo apt-get update

# Install basic dependencies
echo "📦 Installing basic dependencies..."
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
    build-essential \
    python3-pip \
    git

# Install OpenCV
echo "📦 Installing OpenCV..."
sudo apt-get install -y \
    libopencv-dev \
    python3-opencv \
    libopencv-contrib-dev

# Try to install freenect system libraries
echo "📦 Installing freenect system libraries..."
if sudo apt-get install -y libfreenect-dev libfreenect0.5 2>/dev/null; then
    echo "✅ freenect system libraries installed"
else
    echo "⚠️ freenect system libraries not available in repositories"
fi

# Try different freenect installation methods
echo "🔍 Setting up freenect Python bindings..."

# Method 1: Try system package
if sudo apt-get install -y python3-freenect 2>/dev/null; then
    echo "✅ python3-freenect installed from package"
elif test_freenect; then
    echo "✅ freenect already working"
else
    echo "⚠️ python3-freenect not available, trying pip..."
    
    # Method 2: Try pip installation
    if pip3 install freenect 2>/dev/null; then
        echo "✅ freenect installed via pip"
    else
        echo "⚠️ pip installation failed, trying from source..."
        
        # Method 3: Build from source using the GitHub gist method
        echo "🔨 Building freenect from source (GitHub gist method)..."
        
        # Update system first
        sudo apt-get update
        sudo apt-get upgrade -y
        
        # Install dependencies
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
        
        TEMP_DIR=$(mktemp -d)
        cd "$TEMP_DIR"
        
        # Clone and build libfreenect
        git clone git://github.com/OpenKinect/libfreenect.git
        cd libfreenect
        
        mkdir build
        cd build
        
        # Configure and build
        cmake -L ..
        make
        sudo make install
        sudo ldconfig /usr/local/lib64/
        
        # Add user to required groups
        sudo adduser $USER video
        sudo adduser $USER plugdev
        
        # Create udev rules
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
        
        # Install Python bindings
        cd ../wrappers/python
        sudo python3 setup.py install
        
        # Reload udev rules
        sudo udevadm control --reload-rules
        sudo udevadm trigger
        
        cd /
        rm -rf "$TEMP_DIR"
        
        echo "✅ freenect built from source with Python bindings"
    fi
fi

# Install other Python packages
echo "🐍 Installing Python packages..."
pip3 install --upgrade pip
pip3 install \
    opencv-python \
    pillow \
    requests

# Test all installations
echo "🧪 Testing installations..."

echo ""
echo "=== Python Module Tests ==="
python3 -c "
import sys
print('Python version:', sys.version)

modules = [
    ('cv2', 'OpenCV'),
    ('numpy', 'NumPy'),
    ('PIL', 'Pillow'),
    ('requests', 'Requests'),
    ('freenect', 'Freenect')
]

all_good = True
for module, name in modules:
    try:
        __import__(module)
        print(f'✅ {name}: Available')
    except ImportError as e:
        print(f'❌ {name}: Missing - {e}')
        all_good = False

if all_good:
    print('✅ All Python modules available!')
else:
    print('❌ Some Python modules missing')
"

echo ""
echo "=== Freenect Hardware Test ==="
python3 -c "
try:
    import freenect
    print('✅ Freenect Python module available')
    
    ctx = freenect.init()
    if ctx:
        num_devices = freenect.num_devices(ctx)
        print(f'✅ Freenect devices found: {num_devices}')
        
        if num_devices > 0:
            print('✅ Kinect hardware detected!')
        else:
            print('⚠️ No Kinect devices found (connect your Kinect)')
        
        freenect.shutdown(ctx)
    else:
        print('❌ Failed to initialize freenect context')
        
except ImportError:
    print('❌ Freenect Python module not available')
except Exception as e:
    print(f'⚠️ Freenect test error: {e}')
"

echo ""
echo "=== OpenCV Test ==="
python3 -c "
try:
    import cv2
    import numpy as np
    print(f'✅ OpenCV version: {cv2.__version__}')
    
    # Test camera access
    for i in range(3):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret and frame is not None:
                print(f'✅ Camera {i}: Working')
                cap.release()
                break
            cap.release()
    else:
        print('⚠️ No working cameras found')
        
except ImportError:
    print('❌ OpenCV not available')
except Exception as e:
    print(f'⚠️ OpenCV test error: {e}')
"

echo ""
echo "=== System Library Check ==="
# Check for libfreenect
freenect_paths=(
    "/usr/local/lib/libfreenect.so"
    "/usr/lib/libfreenect.so"
    "/usr/lib/x86_64-linux-gnu/libfreenect.so"
    "/usr/lib/arm-linux-gnueabihf/libfreenect.so"
)

freenect_found=false
for path in "${freenect_paths[@]}"; do
    if [ -f "$path" ]; then
        echo "✅ libfreenect found: $path"
        freenect_found=true
        break
    fi
done

if [ "$freenect_found" = false ]; then
    echo "❌ libfreenect system library not found"
fi

# Check USB devices
echo ""
echo "=== Hardware Check ==="
if command -v lsusb &> /dev/null; then
    if lsusb | grep -i microsoft; then
        echo "✅ Microsoft/Kinect device detected"
    else
        echo "⚠️ No Microsoft/Kinect device found in USB devices"
        echo "Available USB devices:"
        lsusb
    fi
else
    echo "❌ lsusb command not available"
fi

echo ""
echo "============================="
echo "📊 SETUP SUMMARY"
echo "============================="

# Final test
if python3 -c "import cv2, numpy, freenect" 2>/dev/null; then
    echo "🎉 SUCCESS! All critical libraries are working!"
    echo ""
    echo "Next steps:"
    echo "1. Connect your Kinect to the Pi"
    echo "2. Run: python3 kinect_unified_streamer.py"
    echo "3. Open http://YOUR_PI_IP:8080 in your browser"
else
    echo "❌ Some libraries are still missing"
    echo ""
    echo "Troubleshooting:"
    echo "1. Check the error messages above"
    echo "2. Make sure your Pi is connected to the internet"
    echo "3. Try running: sudo apt-get update && sudo apt-get upgrade"
    echo "4. For freenect issues, try: bash install_freenect_from_source.sh"
fi

echo ""
echo "Setup complete!"
