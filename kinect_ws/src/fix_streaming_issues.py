#!/usr/bin/env python3
"""
Comprehensive fix for camera streaming issues
This script will diagnose and fix common streaming problems
"""

import requests
import json
import time
import sys
import subprocess
import os

def run_diagnostic(pi_ip, port=8080):
    """Run comprehensive diagnostic on the Pi streaming server"""
    print(f"🔍 Running diagnostic on {pi_ip}:{port}")
    print("=" * 60)
    
    # Check all endpoints
    endpoints = {
        "/": "Root HTML viewer",
        "/stream": "Main stream (what viewer expects)",
        "/rgb": "RGB stream",
        "/status": "Server status",
        "/diagnostic": "Diagnostic info"
    }
    
    results = {}
    
    for endpoint, description in endpoints.items():
        url = f"http://{pi_ip}:{port}{endpoint}"
        try:
            response = requests.get(url, timeout=5)
            results[endpoint] = {
                'status': response.status_code,
                'content_type': response.headers.get('Content-Type', ''),
                'content_length': len(response.content),
                'working': response.status_code == 200
            }
            
            if endpoint == "/status" and response.status_code == 200:
                try:
                    status_data = response.json()
                    results[endpoint]['data'] = status_data
                except:
                    pass
                    
            print(f"✅ {endpoint}: {response.status_code} ({len(response.content)} bytes)")
            
        except Exception as e:
            results[endpoint] = {'working': False, 'error': str(e)}
            print(f"❌ {endpoint}: {e}")
    
    return results

def analyze_issues(results):
    """Analyze diagnostic results and identify issues"""
    print("\n📊 ANALYSIS:")
    print("=" * 60)
    
    issues = []
    recommendations = []
    
    # Check if /stream endpoint works
    if not results.get('/stream', {}).get('working', False):
        issues.append("❌ /stream endpoint not working")
        recommendations.append("🔧 Fix: Check if the correct streaming server is running")
    
    # Check status endpoint
    status_data = results.get('/status', {}).get('data', {})
    if status_data:
        camera_available = status_data.get('camera_available', False)
        kinect_available = status_data.get('kinect_available', False)
        
        if not camera_available and not kinect_available:
            issues.append("❌ No camera or Kinect detected")
            recommendations.append("🔧 Fix: Check camera/Kinect hardware connection")
        
        if status_data.get('kinect_method') == 'freenect_system':
            issues.append("⚠️ Using freenect_system method (may show status frames only)")
            recommendations.append("🔧 Fix: Ensure Kinect hardware is properly connected")
    
    # Check content type
    stream_content_type = results.get('/stream', {}).get('content_type', '')
    if 'image/' not in stream_content_type:
        issues.append("❌ Stream endpoint not serving image data")
        recommendations.append("🔧 Fix: Check streaming server configuration")
    
    return issues, recommendations

def create_fix_script(pi_ip, pi_user="pi"):
    """Create a script to fix streaming issues on the Pi"""
    fix_script = f"""#!/bin/bash
# Auto-generated fix script for streaming issues
# Run this on the Raspberry Pi

echo "🔧 Fixing camera streaming issues..."

# Stop any existing services
sudo systemctl stop camera-stream.service 2>/dev/null || true
sudo systemctl stop kinect-stream.service 2>/dev/null || true

# Kill any existing Python processes
pkill -f "camera_streamer.py" 2>/dev/null || true
pkill -f "kinect_streamer.py" 2>/dev/null || true
pkill -f "kinect_unified_streamer.py" 2>/dev/null || true

# Wait a moment
sleep 2

# Check what camera devices are available
echo "📷 Available video devices:"
ls -la /dev/video* 2>/dev/null || echo "No video devices found"

# Check if Kinect is detected
echo "🎮 Checking for Kinect..."
if command -v freenect-glview >/dev/null 2>&1; then
    echo "freenect tools available"
    freenect-glview --help >/dev/null 2>&1 && echo "Kinect detected" || echo "Kinect not detected"
else
    echo "freenect tools not installed"
fi

# Try to start the appropriate streaming server
echo "🚀 Starting streaming server..."

# First, try the unified streamer (best option)
if [ -f "kinect_unified_streamer.py" ]; then
    echo "Starting unified Kinect streamer..."
    python3 kinect_unified_streamer.py --host 0.0.0.0 --port 8080 &
    STREAMER_PID=$!
    sleep 3
    
    # Test if it's working
    if curl -s http://localhost:8080/status >/dev/null; then
        echo "✅ Unified streamer started successfully"
        echo $STREAMER_PID > /tmp/streamer.pid
        exit 0
    else
        echo "❌ Unified streamer failed, trying camera streamer..."
        kill $STREAMER_PID 2>/dev/null || true
    fi
fi

# Fallback to camera streamer
if [ -f "camera_streamer.py" ]; then
    echo "Starting camera streamer..."
    python3 camera_streamer.py --host 0.0.0.0 --port 8080 &
    STREAMER_PID=$!
    sleep 3
    
    # Test if it's working
    if curl -s http://localhost:8080/status >/dev/null; then
        echo "✅ Camera streamer started successfully"
        echo $STREAMER_PID > /tmp/streamer.pid
        exit 0
    else
        echo "❌ Camera streamer also failed"
        kill $STREAMER_PID 2>/dev/null || true
    fi
fi

echo "❌ All streaming servers failed to start"
exit 1
"""
    
    return fix_script

def main():
    if len(sys.argv) < 2:
        print("Usage: python fix_streaming_issues.py <pi_ip> [pi_user]")
        print("Example: python fix_streaming_issues.py 192.168.1.9")
        sys.exit(1)
    
    pi_ip = sys.argv[1]
    pi_user = sys.argv[2] if len(sys.argv) > 2 else "pi"
    
    print("🔧 Camera Streaming Issue Fixer")
    print("=" * 60)
    
    # Run diagnostic
    results = run_diagnostic(pi_ip)
    
    # Analyze issues
    issues, recommendations = analyze_issues(results)
    
    # Print results
    if issues:
        print("\n🚨 ISSUES FOUND:")
        for issue in issues:
            print(f"  {issue}")
    
    if recommendations:
        print("\n💡 RECOMMENDATIONS:")
        for rec in recommendations:
            print(f"  {rec}")
    
    # Create fix script
    fix_script = create_fix_script(pi_ip, pi_user)
    
    # Save fix script
    fix_script_path = "fix_pi_streaming.sh"
    with open(fix_script_path, 'w') as f:
        f.write(fix_script)
    
    print(f"\n📝 Created fix script: {fix_script_path}")
    print("\n🔧 TO FIX THE ISSUES:")
    print(f"1. Copy the fix script to your Pi:")
    print(f"   scp {fix_script_path} {pi_user}@{pi_ip}:~/")
    print(f"2. SSH to your Pi and run the fix:")
    print(f"   ssh {pi_user}@{pi_ip}")
    print(f"   chmod +x fix_pi_streaming.sh")
    print(f"   ./fix_pi_streaming.sh")
    print(f"3. Test the connection from your Windows machine")
    
    # If we can connect via SSH, offer to run the fix automatically
    print(f"\n🤖 AUTOMATIC FIX (optional):")
    print(f"Would you like me to try to run the fix automatically via SSH?")
    print(f"This requires SSH key authentication to be set up.")
    
    try:
        response = input("Run automatic fix? (y/N): ").strip().lower()
        if response in ['y', 'yes']:
            print("🚀 Running automatic fix...")
            
            # Copy script to Pi
            copy_cmd = f"scp {fix_script_path} {pi_user}@{pi_ip}:~/"
            result = subprocess.run(copy_cmd, shell=True, capture_output=True, text=True)
            if result.returncode != 0:
                print(f"❌ Failed to copy script: {result.stderr}")
                return
            
            # Run script on Pi
            run_cmd = f"ssh {pi_user}@{pi_ip} 'chmod +x fix_pi_streaming.sh && ./fix_pi_streaming.sh'"
            result = subprocess.run(run_cmd, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Fix script executed successfully!")
                print("Output:", result.stdout)
            else:
                print(f"❌ Fix script failed: {result.stderr}")
            
            # Test the fix
            print("\n🧪 Testing the fix...")
            time.sleep(2)
            new_results = run_diagnostic(pi_ip)
            new_issues, new_recommendations = analyze_issues(new_results)
            
            if not new_issues:
                print("🎉 SUCCESS! Streaming issues have been resolved!")
            else:
                print("⚠️ Some issues remain:")
                for issue in new_issues:
                    print(f"  {issue}")
    except KeyboardInterrupt:
        print("\n⏹️ Automatic fix cancelled by user")

if __name__ == "__main__":
    main()
