#!/bin/bash
echo "🔍 Raspberry Pi Library Check"
echo "============================="

# Check Python modules
echo "=== Python Module Check ==="
python3 -c "
import sys
modules = [
    ('cv2', 'OpenCV'),
    ('numpy', 'NumPy'),
    ('PIL', 'Pillow'),
    ('requests', 'Requests'),
    ('threading', 'Threading'),
    ('json', 'JSON'),
    ('base64', 'Base64'),
    ('time', 'Time'),
    ('http.server', 'HTTP Server'),
    ('freenect', 'Freenect (Kinect)')
]

for module, name in modules:
    try:
        __import__(module)
        print(f'✅ {name}: Available')
    except ImportError as e:
        print(f'❌ {name}: Missing - {e}')
"

# Check system libraries
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

# Check for OpenCV system libraries
opencv_paths=(
    "/usr/lib/libopencv_core.so"
    "/usr/lib/x86_64-linux-gnu/libopencv_core.so"
    "/usr/lib/arm-linux-gnueabihf/libopencv_core.so"
)

opencv_found=false
for path in "${opencv_paths[@]}"; do
    if [ -f "$path" ]; then
        echo "✅ OpenCV system library found: $path"
        opencv_found=true
        break
    fi
done

if [ "$opencv_found" = false ]; then
    echo "❌ OpenCV system library not found"
fi

# Check USB devices
echo ""
echo "=== Kinect Hardware Check ==="
if command -v lsusb &> /dev/null; then
    echo "USB devices:"
    lsusb | grep -i microsoft || echo "❌ No Microsoft/Kinect device found in USB devices"
else
    echo "❌ lsusb command not available"
fi

# Check video devices
echo ""
echo "Video devices:"
if ls /dev/video* 2>/dev/null; then
    echo "✅ Video devices found"
else
    echo "❌ No video devices found"
fi

# Test freenect functionality
echo ""
echo "=== Freenect Functionality Test ==="
python3 -c "
try:
    import freenect
    
    # Test freenect initialization
    ctx = freenect.init()
    if ctx:
        print('✅ Freenect context initialized successfully')
        
        # Check for devices
        num_devices = freenect.num_devices(ctx)
        print(f'✅ Number of Kinect devices: {num_devices}')
        
        if num_devices > 0:
            # Try to open device
            device = freenect.open_device(ctx, 0)
            if device:
                print('✅ Kinect device opened successfully')
                freenect.close_device(device)
            else:
                print('❌ Failed to open Kinect device')
        else:
            print('❌ No Kinect devices found')
        
        freenect.shutdown(ctx)
    else:
        print('❌ Failed to initialize freenect context')
        
except ImportError:
    print('❌ Freenect Python module not available')
except Exception as e:
    print(f'❌ Freenect functionality test failed: {e}')
"

# Test OpenCV functionality
echo ""
echo "=== OpenCV Functionality Test ==="
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
                print(f'✅ Camera {i}: Working (frame size: {frame.shape})')
                cap.release()
                break
            else:
                print(f'⚠️ Camera {i}: Opened but no frame')
                cap.release()
        else:
            print(f'❌ Camera {i}: Cannot open')
    
    # Test image operations
    test_image = np.zeros((100, 100, 3), dtype=np.uint8)
    success = cv2.imwrite('/tmp/test_opencv.jpg', test_image)
    if success:
        print('✅ OpenCV image operations working')
        import os
        os.remove('/tmp/test_opencv.jpg')
    else:
        print('❌ OpenCV image operations failed')
        
except ImportError:
    print('❌ OpenCV not available')
except Exception as e:
    print(f'❌ OpenCV functionality test failed: {e}')
"

# Check system packages
echo ""
echo "=== System Package Check ==="
packages=(
    "python3-opencv"
    "python3-freenect"
    "libfreenect-dev"
    "libfreenect0.5"
    "libopencv-dev"
    "python3-pip"
    "python3-dev"
)

for package in "${packages[@]}"; do
    if dpkg -l "$package" 2>/dev/null | grep -q "^ii"; then
        echo "✅ $package: Installed"
    else
        echo "❌ $package: Not installed"
    fi
done

# Check network connectivity
echo ""
echo "=== Network Connectivity Check ==="
if netstat -tuln 2>/dev/null | grep -q ":8080"; then
    echo "⚠️ Port 8080 is in use"
    netstat -tuln | grep ":8080"
else
    echo "✅ Port 8080 is available"
fi

echo ""
echo "============================="
echo "📊 DIAGNOSTIC SUMMARY"
echo "============================="

# Check if critical components are available
if python3 -c "import cv2, numpy, freenect" 2>/dev/null; then
    echo "✅ All critical Python libraries are available!"
    echo "🎯 Your Pi should be ready for Kinect streaming"
else
    echo "❌ Some critical libraries are missing"
    echo ""
    echo "To install missing components, run:"
    echo "bash setup_on_pi.sh"
fi

echo ""
echo "Diagnostic complete"
