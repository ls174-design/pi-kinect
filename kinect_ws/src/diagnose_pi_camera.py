#!/usr/bin/env python3
"""
Diagnostic script to check camera and network status on Raspberry Pi
"""

import cv2
import socket
import subprocess
import sys
import os

def check_camera_devices():
    """Check available camera devices"""
    print("=== Camera Device Check ===")
    
    # Check /dev/video* devices
    try:
        result = subprocess.run(['ls', '/dev/video*'], capture_output=True, text=True)
        if result.returncode == 0:
            print("Available video devices:")
            print(result.stdout)
        else:
            print("No /dev/video* devices found")
    except Exception as e:
        print(f"Error checking video devices: {e}")
    
    # Test OpenCV camera access
    print("\nTesting OpenCV camera access:")
    for i in range(5):  # Test cameras 0-4
        try:
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                ret, frame = cap.read()
                if ret:
                    print(f"✅ Camera {i}: Working (frame size: {frame.shape})")
                else:
                    print(f"⚠️ Camera {i}: Opened but no frame")
                cap.release()
            else:
                print(f"❌ Camera {i}: Cannot open")
        except Exception as e:
            print(f"❌ Camera {i}: Error - {e}")

def check_network_ports():
    """Check network port availability"""
    print("\n=== Network Port Check ===")
    
    # Check if port 8080 is in use
    try:
        result = subprocess.run(['netstat', '-tuln'], capture_output=True, text=True)
        if '8080' in result.stdout:
            print("Port 8080 is in use:")
            for line in result.stdout.split('\n'):
                if '8080' in line:
                    print(f"  {line}")
        else:
            print("Port 8080 is available")
    except Exception as e:
        print(f"Error checking ports: {e}")

def check_python_dependencies():
    """Check Python dependencies"""
    print("\n=== Python Dependencies Check ===")
    
    required_modules = ['cv2', 'numpy', 'requests', 'PIL']
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module}: Available")
        except ImportError as e:
            print(f"❌ {module}: Missing - {e}")

def check_system_resources():
    """Check system resources"""
    print("\n=== System Resources Check ===")
    
    # Check memory
    try:
        with open('/proc/meminfo', 'r') as f:
            meminfo = f.read()
            for line in meminfo.split('\n'):
                if 'MemTotal' in line or 'MemAvailable' in line:
                    print(line)
    except Exception as e:
        print(f"Error checking memory: {e}")
    
    # Check CPU load
    try:
        result = subprocess.run(['uptime'], capture_output=True, text=True)
        print(f"System uptime and load: {result.stdout.strip()}")
    except Exception as e:
        print(f"Error checking uptime: {e}")

def test_simple_camera():
    """Test simple camera capture"""
    print("\n=== Simple Camera Test ===")
    
    try:
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("❌ Cannot open camera 0")
            return False
        
        print("✅ Camera 0 opened successfully")
        
        # Try to read a frame
        ret, frame = cap.read()
        if ret:
            print(f"✅ Frame captured: {frame.shape}")
            
            # Try to save a test image
            cv2.imwrite('/tmp/test_camera.jpg', frame)
            if os.path.exists('/tmp/test_camera.jpg'):
                print("✅ Test image saved successfully")
                os.remove('/tmp/test_camera.jpg')
            else:
                print("❌ Failed to save test image")
        else:
            print("❌ Failed to capture frame")
        
        cap.release()
        return True
        
    except Exception as e:
        print(f"❌ Camera test failed: {e}")
        return False

def main():
    print("Raspberry Pi Camera Diagnostic Tool")
    print("=" * 50)
    
    check_camera_devices()
    check_network_ports()
    check_python_dependencies()
    check_system_resources()
    
    if test_simple_camera():
        print("\n✅ Camera system appears to be working")
    else:
        print("\n❌ Camera system has issues")
    
    print("\n" + "=" * 50)
    print("Diagnostic complete")

if __name__ == '__main__':
    main()
