#!/usr/bin/env python3
"""
Script to restart the Pi streaming service
This will be run on the Pi itself to restart the service
"""

import subprocess
import sys
import time
import os

def restart_streaming_service():
    """Restart the streaming service on the Pi"""
    print("🔄 Restarting Pi streaming service...")
    
    # Kill any existing streaming processes
    try:
        subprocess.run(["pkill", "-f", "kinect_unified_streamer"], check=False)
        subprocess.run(["pkill", "-f", "camera_streamer"], check=False)
        print("✅ Stopped existing streaming processes")
    except Exception as e:
        print(f"⚠️  Warning stopping processes: {e}")
    
    time.sleep(2)
    
    # Change to the correct directory
    os.chdir("/home/ls/kinect_ws/src")
    
    # Start the unified streamer
    try:
        print("🚀 Starting unified Kinect streamer...")
        subprocess.Popen([
            "python3", "kinect_unified_streamer.py", 
            "--host", "0.0.0.0", 
            "--port", "8080"
        ])
        print("✅ Unified Kinect streamer started")
        return True
    except Exception as e:
        print(f"❌ Failed to start unified streamer: {e}")
        
        # Fallback to camera streamer
        try:
            print("🔄 Trying fallback camera streamer...")
            subprocess.Popen([
                "python3", "camera_streamer.py", 
                "--host", "0.0.0.0", 
                "--port", "8080"
            ])
            print("✅ Camera streamer started as fallback")
            return True
        except Exception as e2:
            print(f"❌ Failed to start camera streamer: {e2}")
            return False

if __name__ == "__main__":
    success = restart_streaming_service()
    if success:
        print("🎉 Service restart completed successfully!")
        print("The streaming service should be available at http://192.168.1.9:8080")
    else:
        print("❌ Failed to restart service")
        sys.exit(1)
