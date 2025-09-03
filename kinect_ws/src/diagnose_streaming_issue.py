#!/usr/bin/env python3
"""
Diagnostic script to identify streaming issues
Checks what's actually running on the Pi and what data is being served
"""

import requests
import json
import time
import sys

def check_endpoint(pi_ip, port, endpoint, description):
    """Check a specific endpoint and return status"""
    url = f"http://{pi_ip}:{port}{endpoint}"
    try:
        # Use shorter timeout for faster testing
        response = requests.get(url, timeout=3)
        print(f"✅ {description}:")
        print(f"   URL: {url}")
        print(f"   Status: {response.status_code}")
        print(f"   Content-Type: {response.headers.get('Content-Type', 'Unknown')}")
        print(f"   Content-Length: {len(response.content)} bytes")
        
        if 'application/json' in response.headers.get('Content-Type', ''):
            try:
                data = response.json()
                print(f"   JSON Data: {json.dumps(data, indent=2)}")
            except:
                print(f"   JSON Parse Error")
        elif 'image/' in response.headers.get('Content-Type', ''):
            print(f"   Image data received (size: {len(response.content)} bytes)")
        else:
            print(f"   Raw content preview: {response.text[:100]}...")
        
        return True, response
    except Exception as e:
        print(f"❌ {description}: {e}")
        return False, None

def main():
    if len(sys.argv) != 2:
        print("Usage: python diagnose_streaming_issue.py <pi_ip>")
        print("Example: python diagnose_streaming_issue.py 192.168.1.9")
        sys.exit(1)
    
    pi_ip = sys.argv[1]
    port = 8080
    
    print(f"🔍 Diagnosing streaming issues on {pi_ip}:{port}")
    print("=" * 60)
    
    # Check all possible endpoints
    endpoints = [
        ("/", "Root endpoint (HTML viewer)"),
        ("/stream", "Stream endpoint (what viewer expects)"),
        ("/rgb", "RGB stream endpoint"),
        ("/depth", "Depth stream endpoint"),
        ("/status", "Status endpoint"),
        ("/frame", "Frame endpoint"),
        ("/diagnostic", "Diagnostic endpoint")
    ]
    
    working_endpoints = []
    
    for endpoint, description in endpoints:
        success, response = check_endpoint(pi_ip, port, endpoint, description)
        if success:
            working_endpoints.append((endpoint, description, response))
        print()
    
    print("=" * 60)
    print("📊 SUMMARY:")
    print(f"Working endpoints: {len(working_endpoints)}")
    
    for endpoint, description, response in working_endpoints:
        print(f"  ✅ {endpoint} - {description}")
    
    # Check if the issue is with the viewer's expected endpoint
    stream_working = any(ep[0] == "/stream" for ep in working_endpoints)
    if not stream_working:
        print("\n❌ ISSUE FOUND: /stream endpoint not available!")
        print("   The camera viewer expects /stream but it's not working.")
        print("   Available endpoints:")
        for endpoint, description, _ in working_endpoints:
            print(f"     - {endpoint}")
    
    # Check status data
    status_working = any(ep[0] == "/status" for ep in working_endpoints)
    if status_working:
        print("\n📋 STATUS INFORMATION:")
        for endpoint, description, response in working_endpoints:
            if endpoint == "/status":
                try:
                    data = response.json()
                    print(f"   Server running: {data.get('running', 'Unknown')}")
                    print(f"   Camera available: {data.get('camera_available', 'Unknown')}")
                    print(f"   Frame available: {data.get('frame_available', 'Unknown')}")
                    print(f"   Kinect available: {data.get('kinect_available', 'Unknown')}")
                    print(f"   Kinect method: {data.get('kinect_method', 'Unknown')}")
                except:
                    print("   Could not parse status JSON")
                break

if __name__ == "__main__":
    main()
