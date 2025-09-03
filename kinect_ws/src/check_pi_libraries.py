#!/usr/bin/env python3
"""
Comprehensive library check for Raspberry Pi
Checks all required libraries for Kinect streaming
"""

import sys
import subprocess
import importlib
import os
import glob
import ctypes
from pathlib import Path

def check_python_modules():
    """Check all required Python modules"""
    print("=== Python Module Check ===")
    
    required_modules = [
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
    
    results = {}
    
    for module, name in required_modules:
        try:
            importlib.import_module(module)
            print(f"✅ {name}: Available")
            results[module] = True
        except ImportError as e:
            print(f"❌ {name}: Missing - {e}")
            results[module] = False
    
    return results

def check_system_libraries():
    """Check system libraries"""
    print("\n=== System Library Check ===")
    
    # Check for libfreenect
    freenect_paths = [
        '/usr/local/lib/libfreenect.so',
        '/usr/lib/libfreenect.so',
        '/usr/lib/x86_64-linux-gnu/libfreenect.so',
        '/usr/lib/arm-linux-gnueabihf/libfreenect.so'
    ]
    
    freenect_found = False
    for path in freenect_paths:
        if os.path.exists(path):
            print(f"✅ libfreenect found: {path}")
            freenect_found = True
            break
    
    if not freenect_found:
        print("❌ libfreenect system library not found")
    
    # Check for OpenCV system libraries
    opencv_paths = [
        '/usr/lib/libopencv_core.so',
        '/usr/lib/x86_64-linux-gnu/libopencv_core.so',
        '/usr/lib/arm-linux-gnueabihf/libopencv_core.so'
    ]
    
    opencv_found = False
    for path in opencv_paths:
        if os.path.exists(path):
            print(f"✅ OpenCV system library found: {path}")
            opencv_found = True
            break
    
    if not opencv_found:
        print("❌ OpenCV system library not found")
    
    return freenect_found, opencv_found

def check_kinect_hardware():
    """Check for Kinect hardware"""
    print("\n=== Kinect Hardware Check ===")
    
    # Check USB devices
    try:
        result = subprocess.run(['lsusb'], capture_output=True, text=True)
        if result.returncode == 0:
            usb_devices = result.stdout
            if 'Microsoft' in usb_devices or 'Kinect' in usb_devices:
                print("✅ Kinect device detected in USB devices:")
                for line in usb_devices.split('\n'):
                    if 'Microsoft' in line or 'Kinect' in line:
                        print(f"  {line}")
            else:
                print("❌ No Kinect device found in USB devices")
                print("Available USB devices:")
                for line in usb_devices.split('\n'):
                    if line.strip():
                        print(f"  {line}")
        else:
            print("❌ Cannot run lsusb command")
    except Exception as e:
        print(f"❌ Error checking USB devices: {e}")
    
    # Check video devices
    try:
        video_devices = glob.glob('/dev/video*')
        if video_devices:
            print(f"✅ Video devices found: {video_devices}")
        else:
            print("❌ No video devices found")
    except Exception as e:
        print(f"❌ Error checking video devices: {e}")

def check_freenect_functionality():
    """Test freenect functionality"""
    print("\n=== Freenect Functionality Test ===")
    
    try:
        import freenect
        
        # Test freenect initialization
        ctx = freenect.init()
        if ctx:
            print("✅ Freenect context initialized successfully")
            
            # Check for devices
            num_devices = freenect.num_devices(ctx)
            print(f"✅ Number of Kinect devices: {num_devices}")
            
            if num_devices > 0:
                # Try to open device
                device = freenect.open_device(ctx, 0)
                if device:
                    print("✅ Kinect device opened successfully")
                    
                    # Test video mode
                    try:
                        freenect.set_video_mode(device, freenect.find_video_mode(
                            freenect.RESOLUTION_MEDIUM, freenect.VIDEO_RGB))
                        print("✅ Video mode set successfully")
                    except Exception as e:
                        print(f"⚠️ Video mode setting failed: {e}")
                    
                    # Test depth mode
                    try:
                        freenect.set_depth_mode(device, freenect.find_depth_mode(
                            freenect.RESOLUTION_MEDIUM, freenect.DEPTH_11BIT))
                        print("✅ Depth mode set successfully")
                    except Exception as e:
                        print(f"⚠️ Depth mode setting failed: {e}")
                    
                    freenect.close_device(device)
                else:
                    print("❌ Failed to open Kinect device")
            else:
                print("❌ No Kinect devices found")
            
            freenect.shutdown(ctx)
        else:
            print("❌ Failed to initialize freenect context")
            
    except ImportError:
        print("❌ Freenect Python module not available")
    except Exception as e:
        print(f"❌ Freenect functionality test failed: {e}")

def check_opencv_functionality():
    """Test OpenCV functionality"""
    print("\n=== OpenCV Functionality Test ===")
    
    try:
        import cv2
        import numpy as np
        
        print(f"✅ OpenCV version: {cv2.__version__}")
        
        # Test camera access
        for i in range(3):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                ret, frame = cap.read()
                if ret and frame is not None:
                    print(f"✅ Camera {i}: Working (frame size: {frame.shape})")
                    cap.release()
                    break
                else:
                    print(f"⚠️ Camera {i}: Opened but no frame")
                    cap.release()
            else:
                print(f"❌ Camera {i}: Cannot open")
        
        # Test image operations
        test_image = np.zeros((100, 100, 3), dtype=np.uint8)
        success = cv2.imwrite('/tmp/test_opencv.jpg', test_image)
        if success:
            print("✅ OpenCV image operations working")
            os.remove('/tmp/test_opencv.jpg')
        else:
            print("❌ OpenCV image operations failed")
            
    except ImportError:
        print("❌ OpenCV not available")
    except Exception as e:
        print(f"❌ OpenCV functionality test failed: {e}")

def check_system_packages():
    """Check installed system packages"""
    print("\n=== System Package Check ===")
    
    packages_to_check = [
        'python3-opencv',
        'python3-freenect',
        'libfreenect-dev',
        'libfreenect0.5',
        'libopencv-dev',
        'python3-pip',
        'python3-dev'
    ]
    
    for package in packages_to_check:
        try:
            result = subprocess.run(['dpkg', '-l', package], 
                                  capture_output=True, text=True)
            if result.returncode == 0 and package in result.stdout:
                print(f"✅ {package}: Installed")
            else:
                print(f"❌ {package}: Not installed")
        except Exception as e:
            print(f"⚠️ Cannot check {package}: {e}")

def check_network_connectivity():
    """Check network connectivity"""
    print("\n=== Network Connectivity Check ===")
    
    # Check if port 8080 is available
    try:
        result = subprocess.run(['netstat', '-tuln'], capture_output=True, text=True)
        if '8080' in result.stdout:
            print("⚠️ Port 8080 is in use")
            for line in result.stdout.split('\n'):
                if '8080' in line:
                    print(f"  {line}")
        else:
            print("✅ Port 8080 is available")
    except Exception as e:
        print(f"⚠️ Cannot check port status: {e}")

def generate_install_commands():
    """Generate installation commands for missing components"""
    print("\n=== Installation Commands ===")
    
    print("To install missing components, run these commands:")
    print()
    print("# Update package list")
    print("sudo apt-get update")
    print()
    print("# Install system libraries")
    print("sudo apt-get install -y libfreenect-dev libfreenect0.5")
    print("sudo apt-get install -y python3-freenect")
    print("sudo apt-get install -y python3-opencv")
    print("sudo apt-get install -y libopencv-dev")
    print("sudo apt-get install -y python3-pip python3-dev")
    print()
    print("# Install Python packages")
    print("pip3 install opencv-python numpy pillow requests")
    print("pip3 install freenect")
    print()
    print("# Update library cache")
    print("sudo ldconfig")

def main():
    print("🔍 Raspberry Pi Library Diagnostic Tool")
    print("=" * 60)
    
    # Run all checks
    python_results = check_python_modules()
    freenect_sys, opencv_sys = check_system_libraries()
    check_kinect_hardware()
    check_freenect_functionality()
    check_opencv_functionality()
    check_system_packages()
    check_network_connectivity()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 DIAGNOSTIC SUMMARY")
    print("=" * 60)
    
    critical_modules = ['cv2', 'numpy', 'freenect']
    critical_available = all(python_results.get(module, False) for module in critical_modules)
    
    if critical_available and freenect_sys and opencv_sys:
        print("✅ All critical libraries are available!")
        print("🎯 Your Pi should be ready for Kinect streaming")
    else:
        print("❌ Some critical libraries are missing")
        print("\nMissing components:")
        
        if not python_results.get('cv2', False):
            print("  - OpenCV Python module")
        if not python_results.get('numpy', False):
            print("  - NumPy Python module")
        if not python_results.get('freenect', False):
            print("  - Freenect Python module")
        if not freenect_sys:
            print("  - libfreenect system library")
        if not opencv_sys:
            print("  - OpenCV system library")
        
        generate_install_commands()
    
    print("\n" + "=" * 60)
    print("Diagnostic complete")

if __name__ == '__main__':
    main()
