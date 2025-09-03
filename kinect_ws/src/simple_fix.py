#!/usr/bin/env python3
"""
Simple fix: Force the service to use OpenCV instead of freenect
This will work if there's a regular USB camera available
"""

import os
import shutil

def apply_simple_fix():
    """Apply a simple fix to use OpenCV instead of freenect"""
    print("🔧 Applying simple fix (force OpenCV)...")
    
    # Backup the current file
    if os.path.exists("kinect_unified_streamer.py"):
        shutil.copy("kinect_unified_streamer.py", "kinect_unified_streamer.py.backup3")
        print("✅ Created backup of current file")
    
    # Read the current file
    with open("kinect_unified_streamer.py", "r") as f:
        content = f.read()
    
    # Change the kinect method detection to force OpenCV
    old_detection = '''            # Try freenect first
            if self._try_freenect():
                self.kinect_method = 'freenect'
                print("✅ Using freenect for Kinect capture")
            elif self._try_freenect_system():
                self.kinect_method = 'freenect_system'
                print("✅ Using freenect system for Kinect capture")
            elif self._try_opencv():
                self.kinect_method = 'opencv'
                print("✅ Using OpenCV for camera capture")
            else:
                self.kinect_method = None
                print("❌ No suitable capture method found")'''
    
    new_detection = '''            # Try OpenCV first (more reliable)
            if self._try_opencv():
                self.kinect_method = 'opencv'
                print("✅ Using OpenCV for camera capture")
            elif self._try_freenect():
                self.kinect_method = 'freenect'
                print("✅ Using freenect for Kinect capture")
            elif self._try_freenect_system():
                self.kinect_method = 'freenect_system'
                print("✅ Using freenect system for Kinect capture")
            else:
                self.kinect_method = None
                print("❌ No suitable capture method found")'''
    
    if old_detection in content:
        content = content.replace(old_detection, new_detection)
        print("✅ Applied simple fix - OpenCV will be tried first")
    else:
        print("⚠️  Could not find detection code - may already be modified")
    
    # Write the fixed file
    with open("kinect_unified_streamer.py", "w") as f:
        f.write(content)
    
    print("✅ Simple fix applied")
    return True

def restart_service():
    """Restart the streaming service"""
    print("🔄 Restarting streaming service...")
    
    # Kill existing processes
    os.system("pkill -f kinect_unified_streamer")
    os.system("pkill -f camera_streamer")
    time.sleep(2)
    
    # Start the service
    os.system("python3 kinect_unified_streamer.py --host 0.0.0.0 --port 8080 &")
    print("✅ Service restarted")

if __name__ == "__main__":
    print("🚀 Applying simple fix (OpenCV first)...")
    
    # Change to the correct directory
    os.chdir("/home/ls/kinect_ws/src")
    
    # Apply the fix
    if apply_simple_fix():
        # Restart the service
        restart_service()
        print("🎉 Simple fix applied and service restarted!")
        print("The service will now try OpenCV first, which is more reliable.")
    else:
        print("❌ Fix could not be applied")
