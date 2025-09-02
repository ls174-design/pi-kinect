#!/usr/bin/env python3
"""
Test script to verify the camera streaming setup
"""

import sys
import subprocess
import importlib

def test_imports():
    """Test if all required modules can be imported"""
    print("Testing Python module imports...")
    
    modules = [
        ('cv2', 'OpenCV'),
        ('numpy', 'NumPy'),
        ('PIL', 'Pillow'),
        ('requests', 'Requests'),
        ('tkinter', 'Tkinter'),
        ('threading', 'Threading'),
        ('json', 'JSON'),
        ('base64', 'Base64'),
        ('io', 'IO'),
        ('time', 'Time')
    ]
    
    failed_imports = []
    
    for module, name in modules:
        try:
            importlib.import_module(module)
            print(f"✓ {name} - OK")
        except ImportError as e:
            print(f"✗ {name} - FAILED: {e}")
            failed_imports.append(name)
    
    if failed_imports:
        print(f"\nFailed imports: {', '.join(failed_imports)}")
        return False
    else:
        print("\n✓ All required modules imported successfully!")
        return True

def test_camera_availability():
    """Test if camera is available"""
    print("\nTesting camera availability...")
    
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                print("✓ Camera 0 is available and working")
                cap.release()
                return True
            else:
                print("✗ Camera 0 opened but cannot read frames")
                cap.release()
                return False
        else:
            print("✗ Camera 0 is not available")
            return False
    except Exception as e:
        print(f"✗ Error testing camera: {e}")
        return False

def test_network_connectivity():
    """Test network connectivity to Raspberry Pi"""
    print("\nTesting network connectivity...")
    
    pi_ip = "192.168.1.9"  # Default Pi IP
    
    try:
        import subprocess
        result = subprocess.run(['ping', '-n', '1', pi_ip], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print(f"✓ Can ping Raspberry Pi at {pi_ip}")
            return True
        else:
            print(f"✗ Cannot ping Raspberry Pi at {pi_ip}")
            return False
    except Exception as e:
        print(f"✗ Error testing network connectivity: {e}")
        return False

def test_http_connectivity():
    """Test HTTP connectivity to Raspberry Pi"""
    print("\nTesting HTTP connectivity...")
    
    pi_ip = "192.168.1.9"
    port = 8080
    
    try:
        import requests
        url = f"http://{pi_ip}:{port}/status"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            print(f"✓ Camera streaming server is running on {pi_ip}:{port}")
            return True
        else:
            print(f"✗ Camera streaming server returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"✗ Cannot connect to camera streaming server on {pi_ip}:{port}")
        print("  Make sure the server is running on the Raspberry Pi")
        return False
    except Exception as e:
        print(f"✗ Error testing HTTP connectivity: {e}")
        return False

def main():
    print("=" * 50)
    print("Camera Streaming Setup Test")
    print("=" * 50)
    
    tests = [
        ("Module Imports", test_imports),
        ("Camera Availability", test_camera_availability),
        ("Network Connectivity", test_network_connectivity),
        ("HTTP Connectivity", test_http_connectivity)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        print("-" * 30)
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ Test failed with error: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Your setup is ready.")
        print("\nNext steps:")
        print("1. Run: python windows_camera_viewer.py")
        print("2. Or open: http://192.168.1.9:8080 in your browser")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please check the issues above.")
        
        if not results[0][1]:  # Module imports failed
            print("\nTo fix module import issues:")
            print("pip install -r requirements.txt")
        
        if not results[2][1]:  # Network connectivity failed
            print("\nTo fix network connectivity:")
            print("1. Check your Raspberry Pi IP address")
            print("2. Make sure both devices are on the same network")
            print("3. Update the IP in the scripts if needed")
        
        if not results[3][1]:  # HTTP connectivity failed
            print("\nTo fix HTTP connectivity:")
            print("1. Make sure the camera streaming server is running on Pi")
            print("2. Run: python sync_to_pi.py --pi-host YOUR_PI_IP --start-service")

if __name__ == '__main__':
    main()
