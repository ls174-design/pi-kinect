#!/usr/bin/env python3
"""
Detailed diagnostic to understand why stream endpoint returns 503
"""

import requests
import json
import sys

def detailed_diagnostic(pi_ip, port=8080):
    """Detailed diagnostic of the streaming service"""
    print(f"🔍 Detailed diagnostic of streaming service on {pi_ip}:{port}")
    print("=" * 60)
    
    # Test status endpoint for detailed info
    try:
        print("1. Checking status endpoint...")
        response = requests.get(f"http://{pi_ip}:{port}/status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ Status endpoint working")
            print(f"   Kinect available: {data.get('kinect_available')}")
            print(f"   Kinect method: {data.get('kinect_method')}")
            print(f"   Frame count: {data.get('frame_count')}")
            print(f"   FPS: {data.get('fps', 0):.1f}")
            print(f"   Running: {data.get('running')}")
            print(f"   Error message: {data.get('error_message')}")
        else:
            print(f"❌ Status endpoint failed: HTTP {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Status endpoint error: {e}")
        return
    
    print()
    
    # Test frame endpoint
    try:
        print("2. Checking frame endpoint...")
        response = requests.get(f"http://{pi_ip}:{port}/frame", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ Frame endpoint working")
            print(f"   RGB available: {data.get('rgb_available')}")
            print(f"   Depth available: {data.get('depth_available')}")
            print(f"   Kinect available: {data.get('kinect_available')}")
            print(f"   RGB data size: {len(data.get('rgb_data', ''))}")
        else:
            print(f"❌ Frame endpoint failed: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ Frame endpoint error: {e}")
    
    print()
    
    # Test stream endpoint
    try:
        print("3. Checking stream endpoint...")
        response = requests.get(f"http://{pi_ip}:{port}/stream", timeout=5)
        print(f"   Status code: {response.status_code}")
        print(f"   Content length: {len(response.content)}")
        print(f"   Content type: {response.headers.get('Content-Type')}")
        
        if response.status_code == 200:
            print("✅ Stream endpoint working - real image data!")
        elif response.status_code == 503:
            print("❌ Stream endpoint returns 503 - Service Unavailable")
            print("   This usually means get_frame() is returning None")
        else:
            print(f"❌ Stream endpoint failed: HTTP {response.status_code}")
            
    except Exception as e:
        print(f"❌ Stream endpoint error: {e}")
    
    print()
    
    # Test diagnostic endpoint
    try:
        print("4. Checking diagnostic endpoint...")
        response = requests.get(f"http://{pi_ip}:{port}/diagnostic", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ Diagnostic endpoint working")
            print(f"   Stream type: {data.get('stream_type')}")
            print(f"   Server running: {data.get('server_running')}")
            print(f"   Kinect available: {data.get('kinect_available')}")
            print(f"   Kinect method: {data.get('kinect_method')}")
            print(f"   Error message: {data.get('error_message')}")
        else:
            print(f"❌ Diagnostic endpoint failed: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ Diagnostic endpoint error: {e}")
    
    print()
    print("=" * 60)
    print("DIAGNOSIS:")
    print("If stream endpoint returns 503, the issue is likely:")
    print("1. get_frame() is returning None")
    print("2. The freenect capture is not working properly")
    print("3. The frame capture thread is not running")
    print()
    print("SOLUTION:")
    print("Check the Pi console for error messages when starting the service")
    print("The service should show frame capture progress every 100 frames")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python detailed_diagnostic.py <pi_ip>")
        sys.exit(1)
    
    pi_ip = sys.argv[1]
    detailed_diagnostic(pi_ip)
