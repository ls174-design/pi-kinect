#!/usr/bin/env python3
"""
Remote driver check - can be run from Windows to check Pi status
"""

import requests
import json
import sys

def check_pi_drivers(pi_ip, port=8080):
    """Check Pi driver status remotely"""
    print(f"🔍 Remote driver check for Pi at {pi_ip}:{port}")
    print("="*60)
    
    # Check if the service is running
    try:
        response = requests.get(f"http://{pi_ip}:{port}/diagnostic", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ Pi streaming service is running")
            print(f"   Stream type: {data.get('stream_type')}")
            print(f"   Kinect available: {data.get('kinect_available')}")
            print(f"   Kinect method: {data.get('kinect_method')}")
            print(f"   Error message: {data.get('error_message')}")
            print(f"   Freenect Python available: {data.get('freenect_python_available')}")
            print(f"   Available video devices: {data.get('available_video_devices')}")
        else:
            print(f"❌ Pi service not responding: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to Pi: {e}")
        return False
    
    print("\n📋 RECOMMENDATIONS:")
    
    if not data.get('kinect_available'):
        print("• Kinect is not detected by the Pi")
        print("• Check USB connection and power")
        print("• Try different USB port")
    
    if not data.get('freenect_python_available'):
        print("• Freenect Python bindings are not available")
        print("• Install with: pip3 install freenect")
    
    if data.get('kinect_method') == 'freenect_system' and data.get('frame_count', 0) == 0:
        print("• Kinect is detected but not capturing frames")
        print("• This indicates a freenect driver issue")
        print("• Try running the driver check script on the Pi")
    
    if not data.get('available_video_devices'):
        print("• No video devices detected")
        print("• Check camera connections")
    
    return True

def main():
    if len(sys.argv) != 2:
        print("Usage: python remote_driver_check.py <pi_ip>")
        print("Example: python remote_driver_check.py 192.168.1.9")
        sys.exit(1)
    
    pi_ip = sys.argv[1]
    check_pi_drivers(pi_ip)

if __name__ == "__main__":
    main()
