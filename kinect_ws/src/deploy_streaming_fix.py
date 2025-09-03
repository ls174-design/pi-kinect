#!/usr/bin/env python3
"""
Deploy the streaming fix to the Raspberry Pi
"""

import subprocess
import sys
import os

def deploy_fix(pi_ip, pi_user="pi"):
    """Deploy the fixed streaming code to the Pi"""
    print(f"🚀 Deploying streaming fix to {pi_user}@{pi_ip}")
    
    # Files to deploy
    files_to_deploy = [
        "kinect_unified_streamer.py",
        "windows_camera_viewer.py"
    ]
    
    for file in files_to_deploy:
        if os.path.exists(file):
            print(f"📤 Deploying {file}...")
            cmd = f"scp {file} {pi_user}@{pi_ip}:~/kinect_ws/src/"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ {file} deployed successfully")
            else:
                print(f"❌ Failed to deploy {file}: {result.stderr}")
        else:
            print(f"⚠️ {file} not found, skipping")
    
    print("\n🔄 Restarting streaming service...")
    
    # Restart the streaming service
    restart_cmd = f"ssh {pi_user}@{pi_ip} 'pkill -f kinect_unified_streamer.py; sleep 2; cd ~/kinect_ws/src && python3 kinect_unified_streamer.py --host 0.0.0.0 --port 8080 &'"
    result = subprocess.run(restart_cmd, shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        print("✅ Streaming service restarted")
    else:
        print(f"❌ Failed to restart service: {result.stderr}")
    
    print("\n🧪 Testing the fix...")
    import time
    time.sleep(3)
    
    # Test the status endpoint
    test_cmd = f"curl -s http://{pi_ip}:8080/status"
    result = subprocess.run(test_cmd, shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        print("✅ Status endpoint working")
        print("Status response:", result.stdout[:200] + "..." if len(result.stdout) > 200 else result.stdout)
    else:
        print(f"❌ Status endpoint test failed: {result.stderr}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python deploy_streaming_fix.py <pi_ip> [pi_user]")
        print("Example: python deploy_streaming_fix.py 192.168.1.9")
        sys.exit(1)
    
    pi_ip = sys.argv[1]
    pi_user = sys.argv[2] if len(sys.argv) > 2 else "pi"
    
    deploy_fix(pi_ip, pi_user)

if __name__ == "__main__":
    main()
