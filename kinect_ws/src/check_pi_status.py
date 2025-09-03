#!/usr/bin/env python3
"""
Quick script to check Pi status and streaming service
"""

import requests
import subprocess
import sys

def check_pi_connectivity(pi_host):
    """Check if Pi is reachable"""
    print(f"🔍 Checking connectivity to {pi_host}...")
    
    try:
        result = subprocess.run(['ping', '-n', '1', pi_host], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("✅ Pi is reachable via ping")
            return True
        else:
            print("❌ Pi is not reachable via ping")
            return False
    except Exception as e:
        print(f"❌ Ping test failed: {e}")
        return False

def check_streaming_service(pi_host, port=8080):
    """Check if streaming service is running"""
    print(f"🌐 Checking streaming service at {pi_host}:{port}...")
    
    try:
        response = requests.get(f'http://{pi_host}:{port}/status', timeout=5)
        if response.status_code == 200:
            print("✅ Streaming service is running")
            status = response.json()
            print(f"📊 Service status: {status}")
            return True
        else:
            print(f"⚠️ Streaming service returned status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectTimeout:
        print("❌ Connection timeout - streaming service not responding")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ Connection refused - streaming service not running")
        return False
    except Exception as e:
        print(f"❌ Error checking streaming service: {e}")
        return False

def main():
    print("🔍 Pi Status Checker")
    print("=" * 30)
    
    pi_host = input("Enter Pi IP address (default: 192.168.1.9): ").strip() or "192.168.1.9"
    
    print(f"\n📡 Checking Pi at {pi_host}...")
    
    # Check connectivity
    if not check_pi_connectivity(pi_host):
        print("\n❌ Pi Status: OFFLINE")
        print("💡 Solutions:")
        print("   - Check if Pi is powered on")
        print("   - Check network connection")
        print("   - Verify IP address")
        sys.exit(1)
    
    # Check streaming service
    if check_streaming_service(pi_host):
        print("\n🎉 Pi Status: ONLINE - Streaming service running")
        print(f"📺 Stream available at: http://{pi_host}:8080")
        print("💡 You can now use the camera viewer")
    else:
        print("\n⚠️ Pi Status: ONLINE - Streaming service not running")
        print("💡 Solutions:")
        print("   - Run: start_pi_streaming.bat")
        print("   - Or SSH to Pi and run: python3 kinect_unified_streamer.py")

if __name__ == '__main__':
    main()
