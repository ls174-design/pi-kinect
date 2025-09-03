#!/usr/bin/env python3
"""
Apply the streaming fix to the Pi
This script fixes the kinect_method detection issue
"""

import os
import shutil
import time

def apply_fix():
    """Apply the streaming fix"""
    print("🔧 Applying streaming fix...")
    
    # Backup the original file
    if os.path.exists("kinect_unified_streamer.py"):
        shutil.copy("kinect_unified_streamer.py", "kinect_unified_streamer.py.backup")
        print("✅ Created backup of original file")
    
    # Read the current file
    with open("kinect_unified_streamer.py", "r") as f:
        content = f.read()
    
    # Apply the fix
    old_code = """                if self.kinect_method == 'freenect':
                    self._capture_freenect_frames()
                elif self.kinect_method == 'opencv':
                    self._capture_opencv_frames()
                else:"""
    
    new_code = """                if self.kinect_method in ['freenect', 'freenect_system']:
                    self._capture_freenect_frames()
                elif self.kinect_method == 'opencv':
                    self._capture_opencv_frames()
                else:"""
    
    if old_code in content:
        content = content.replace(old_code, new_code)
        
        # Write the fixed file
        with open("kinect_unified_streamer.py", "w") as f:
            f.write(content)
        
        print("✅ Applied the kinect_method detection fix")
        return True
    else:
        print("⚠️  Fix already applied or code structure changed")
        return False

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
    print("🚀 Applying streaming fix to Pi...")
    
    # Change to the correct directory
    os.chdir("/home/ls/kinect_ws/src")
    
    # Apply the fix
    if apply_fix():
        # Restart the service
        restart_service()
        print("🎉 Fix applied and service restarted!")
        print("The camera should now show real image data instead of status frames.")
    else:
        print("❌ Fix could not be applied")
