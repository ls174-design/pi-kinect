#!/usr/bin/env python3
"""
Comprehensive driver and dependency check for Kinect on Raspberry Pi
This script will check all necessary components for Kinect operation
"""

import subprocess
import sys
import os

def run_command(cmd, description):
    """Run a command and return the result"""
    print(f"🔍 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✅ {description}: OK")
            if result.stdout.strip():
                print(f"   Output: {result.stdout.strip()}")
            return True, result.stdout
        else:
            print(f"❌ {description}: FAILED")
            if result.stderr.strip():
                print(f"   Error: {result.stderr.strip()}")
            return False, result.stderr
    except subprocess.TimeoutExpired:
        print(f"⏰ {description}: TIMEOUT")
        return False, "Command timed out"
    except Exception as e:
        print(f"❌ {description}: ERROR - {e}")
        return False, str(e)

def check_python_packages():
    """Check if required Python packages are installed"""
    print("\n" + "="*60)
    print("PYTHON PACKAGES CHECK")
    print("="*60)
    
    packages = [
        ("cv2", "OpenCV"),
        ("numpy", "NumPy"),
        ("freenect", "Freenect Python bindings"),
        ("requests", "Requests"),
        ("PIL", "Pillow")
    ]
    
    results = {}
    for package, name in packages:
        try:
            __import__(package)
            print(f"✅ {name}: Installed")
            results[package] = True
        except ImportError:
            print(f"❌ {name}: NOT INSTALLED")
            results[package] = False
    
    return results

def check_system_dependencies():
    """Check system-level dependencies"""
    print("\n" + "="*60)
    print("SYSTEM DEPENDENCIES CHECK")
    print("="*60)
    
    checks = [
        ("which freenect", "Freenect command line tools"),
        ("which freenect-glview", "Freenect GL viewer"),
        ("which freenect-record", "Freenect recording tool"),
        ("lsusb | grep -i kinect", "Kinect USB device detection"),
        ("lsusb | grep -i microsoft", "Microsoft USB devices"),
        ("lsmod | grep -i usb", "USB kernel modules"),
        ("lsmod | grep -i video", "Video kernel modules"),
        ("ls /dev/video*", "Video devices"),
        ("ls /dev/bus/usb", "USB bus devices")
    ]
    
    results = {}
    for cmd, description in checks:
        success, output = run_command(cmd, description)
        results[description] = success
    
    return results

def check_freenect_installation():
    """Check freenect installation details"""
    print("\n" + "="*60)
    print("FREENECT INSTALLATION CHECK")
    print("="*60)
    
    checks = [
        ("freenect --version", "Freenect version"),
        ("pkg-config --modversion libfreenect", "Libfreenect version"),
        ("ldconfig -p | grep freenect", "Freenect libraries"),
        ("find /usr -name '*freenect*' 2>/dev/null | head -10", "Freenect files"),
        ("python3 -c 'import freenect; print(freenect.__file__)'", "Freenect Python module location")
    ]
    
    results = {}
    for cmd, description in checks:
        success, output = run_command(cmd, description)
        results[description] = success
    
    return results

def check_usb_permissions():
    """Check USB permissions and udev rules"""
    print("\n" + "="*60)
    print("USB PERMISSIONS CHECK")
    print("="*60)
    
    checks = [
        ("groups $USER", "Current user groups"),
        ("ls -la /dev/bus/usb/", "USB device permissions"),
        ("ls -la /etc/udev/rules.d/ | grep -i kinect", "Kinect udev rules"),
        ("ls -la /etc/udev/rules.d/ | grep -i freenect", "Freenect udev rules"),
        ("id", "User ID and groups")
    ]
    
    results = {}
    for cmd, description in checks:
        success, output = run_command(cmd, description)
        results[description] = success
    
    return results

def check_kinect_detection():
    """Check if Kinect is detected by the system"""
    print("\n" + "="*60)
    print("KINECT DETECTION CHECK")
    print("="*60)
    
    checks = [
        ("lsusb -v | grep -A 10 -B 5 -i kinect", "Detailed Kinect USB info"),
        ("lsusb -v | grep -A 10 -B 5 -i microsoft", "Microsoft device info"),
        ("dmesg | grep -i kinect | tail -5", "Kernel messages about Kinect"),
        ("dmesg | grep -i usb | tail -10", "Recent USB kernel messages")
    ]
    
    results = {}
    for cmd, description in checks:
        success, output = run_command(cmd, description)
        results[description] = success
    
    return results

def test_freenect_python():
    """Test freenect Python functionality"""
    print("\n" + "="*60)
    print("FREENECT PYTHON TEST")
    print("="*60)
    
    test_code = '''
import freenect
import sys

try:
    print("Testing freenect Python module...")
    
    # Test basic freenect functions
    print("1. Testing freenect.init()...")
    ctx = freenect.init()
    print(f"   Context created: {ctx is not None}")
    
    print("2. Testing freenect.num_devices()...")
    num_devices = freenect.num_devices(ctx)
    print(f"   Number of devices: {num_devices}")
    
    if num_devices > 0:
        print("3. Testing device access...")
        device = freenect.open_device(ctx, 0)
        print(f"   Device opened: {device is not None}")
        
        if device:
            print("4. Testing video format...")
            freenect.set_video_format(device, freenect.VIDEO_RGB)
            print("   Video format set to RGB")
            
            print("5. Testing depth format...")
            freenect.set_depth_format(device, freenect.DEPTH_11BIT)
            print("   Depth format set to 11-bit")
            
            freenect.close_device(device)
            print("   Device closed")
    else:
        print("   No Kinect devices found")
    
    freenect.shutdown(ctx)
    print("   Context shutdown")
    
    print("✅ Freenect Python test completed successfully")
    
except Exception as e:
    print(f"❌ Freenect Python test failed: {e}")
    sys.exit(1)
'''
    
    try:
        result = subprocess.run([sys.executable, "-c", test_code], 
                              capture_output=True, text=True, timeout=30)
        print(result.stdout)
        if result.stderr:
            print("Errors:")
            print(result.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Failed to run freenect test: {e}")
        return False

def generate_report(python_results, system_results, freenect_results, usb_results, detection_results, freenect_test):
    """Generate a comprehensive report"""
    print("\n" + "="*60)
    print("COMPREHENSIVE REPORT")
    print("="*60)
    
    print("\n📊 SUMMARY:")
    
    # Python packages
    python_ok = sum(python_results.values())
    python_total = len(python_results)
    print(f"Python packages: {python_ok}/{python_total} installed")
    
    # System dependencies
    system_ok = sum(system_results.values())
    system_total = len(system_results)
    print(f"System dependencies: {system_ok}/{system_total} available")
    
    # Freenect installation
    freenect_ok = sum(freenect_results.values())
    freenect_total = len(freenect_results)
    print(f"Freenect installation: {freenect_ok}/{freenect_total} components found")
    
    # USB permissions
    usb_ok = sum(usb_results.values())
    usb_total = len(usb_results)
    print(f"USB permissions: {usb_ok}/{usb_total} checks passed")
    
    # Kinect detection
    detection_ok = sum(detection_results.values())
    detection_total = len(detection_results)
    print(f"Kinect detection: {detection_ok}/{detection_total} checks passed")
    
    print(f"Freenect Python test: {'✅ PASSED' if freenect_test else '❌ FAILED'}")
    
    print("\n🔧 RECOMMENDATIONS:")
    
    if not python_results.get('freenect', False):
        print("• Install freenect Python bindings: pip3 install freenect")
    
    if not system_results.get('Freenect command line tools', False):
        print("• Install freenect: sudo apt-get install freenect")
    
    if not detection_results.get('Detailed Kinect USB info', False):
        print("• Check Kinect USB connection and power")
        print("• Try different USB port or USB hub")
    
    if not usb_results.get('Current user groups', False):
        print("• Add user to video group: sudo usermod -a -G video $USER")
        print("• Add user to plugdev group: sudo usermod -a -G plugdev $USER")
    
    if not freenect_test:
        print("• Freenect Python module is not working properly")
        print("• Try reinstalling: sudo apt-get remove freenect && sudo apt-get install freenect")
        print("• Reinstall Python bindings: pip3 uninstall freenect && pip3 install freenect")

def main():
    """Main diagnostic function"""
    print("🔍 KINECT DRIVER AND DEPENDENCY CHECK")
    print("="*60)
    print("This script will check all components needed for Kinect operation")
    print()
    
    # Run all checks
    python_results = check_python_packages()
    system_results = check_system_dependencies()
    freenect_results = check_freenect_installation()
    usb_results = check_usb_permissions()
    detection_results = check_kinect_detection()
    freenect_test = test_freenect_python()
    
    # Generate report
    generate_report(python_results, system_results, freenect_results, 
                   usb_results, detection_results, freenect_test)
    
    print("\n" + "="*60)
    print("DIAGNOSTIC COMPLETE")
    print("="*60)

if __name__ == "__main__":
    main()
