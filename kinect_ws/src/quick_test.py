#!/usr/bin/env python3
"""
Quick test script to check if the streaming fix worked
Only tests essential endpoints with limited data
"""

import requests
import json
import sys

def quick_test(pi_ip, port=8080):
    """Quick test of the streaming service"""
    print(f"🔍 Quick test of streaming service on {pi_ip}:{port}")
    print("=" * 50)
    
    # Test only the essential endpoints
    endpoints = {
        "/status": "Status endpoint",
        "/stream": "Stream endpoint (main test)"
    }
    
    results = {}
    
    for endpoint, description in endpoints.items():
        url = f"http://{pi_ip}:{port}{endpoint}"
        try:
            print(f"Testing {description}...")
            response = requests.get(url, timeout=3)
            
            if response.status_code == 200:
                print(f"✅ {description}: OK")
                
                if endpoint == "/status":
                    try:
                        data = response.json()
                        print(f"   Kinect available: {data.get('kinect_available', 'Unknown')}")
                        print(f"   Kinect method: {data.get('kinect_method', 'Unknown')}")
                        print(f"   Frame count: {data.get('frame_count', 'Unknown')}")
                        print(f"   FPS: {data.get('fps', 'Unknown'):.1f}" if data.get('fps') else "   FPS: Unknown")
                    except:
                        print("   Status data: Available but not JSON")
                
                elif endpoint == "/stream":
                    print(f"   Image data: {len(response.content)} bytes")
                    if len(response.content) > 1000:
                        print("   ✅ Real image data detected!")
                    else:
                        print("   ⚠️  Small data size - might be status frame")
                
                results[endpoint] = True
            else:
                print(f"❌ {description}: HTTP {response.status_code}")
                results[endpoint] = False
                
        except requests.exceptions.Timeout:
            print(f"⏰ {description}: Timeout")
            results[endpoint] = False
        except requests.exceptions.ConnectionError:
            print(f"❌ {description}: Connection refused")
            results[endpoint] = False
        except Exception as e:
            print(f"❌ {description}: Error - {e}")
            results[endpoint] = False
        
        print()
    
    # Summary
    print("=" * 50)
    working = sum(results.values())
    total = len(results)
    
    if working == total:
        print("🎉 ALL TESTS PASSED! The streaming fix is working!")
        print("The camera viewer should now show real camera data.")
    elif working > 0:
        print(f"⚠️  PARTIAL SUCCESS: {working}/{total} endpoints working")
        print("Some functionality is available but there may be issues.")
    else:
        print("❌ ALL TESTS FAILED: Service is not responding")
        print("Check if the service is running on the Pi.")
    
    return working == total

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python quick_test.py <pi_ip>")
        print("Example: python quick_test.py 192.168.1.9")
        sys.exit(1)
    
    pi_ip = sys.argv[1]
    success = quick_test(pi_ip)
    sys.exit(0 if success else 1)
