#!/usr/bin/env python3
"""
Fix script for freenect capture issues
This script will modify the unified streamer to handle freenect capture problems
"""

import os
import shutil

def apply_freenect_fix():
    """Apply the freenect capture fix"""
    print("🔧 Applying freenect capture fix...")
    
    # Backup the current file
    if os.path.exists("kinect_unified_streamer.py"):
        shutil.copy("kinect_unified_streamer.py", "kinect_unified_streamer.py.backup2")
        print("✅ Created backup of current file")
    
    # Read the current file
    with open("kinect_unified_streamer.py", "r") as f:
        content = f.read()
    
    # Fix 1: Add better error handling in _capture_freenect_frames
    old_capture_method = '''    def _capture_freenect_frames(self):
        """Capture frames using freenect"""
        try:
            if self.freenect_ctx and self.freenect_device:
                # Process freenect events
                freenect.process_events(self.freenect_ctx)
                
                # Get RGB frame
                rgb_data = freenect.sync_get_video()[0]
                if rgb_data is not None:
                    frame = rgb_data.reshape((480, 640, 3))
                    with self.lock:
                        self.frame = frame
                    self.frame_count += 1
                
                # Get depth frame
                depth_data = freenect.sync_get_depth()[0]
                if depth_data is not None:
                    with self.lock:
                        self.depth_frame = depth_data
        except Exception as e:
            print(f"Error capturing freenect frames: {e}")'''
    
    new_capture_method = '''    def _capture_freenect_frames(self):
        """Capture frames using freenect"""
        try:
            if self.freenect_ctx and self.freenect_device:
                # Process freenect events
                freenect.process_events(self.freenect_ctx)
                
                # Get RGB frame with retry logic
                rgb_data = None
                for attempt in range(3):  # Try 3 times
                    try:
                        rgb_data = freenect.sync_get_video()[0]
                        if rgb_data is not None:
                            break
                    except Exception as e:
                        if attempt == 2:  # Last attempt
                            print(f"Failed to get RGB frame after 3 attempts: {e}")
                        continue
                
                if rgb_data is not None:
                    frame = rgb_data.reshape((480, 640, 3))
                    with self.lock:
                        self.frame = frame
                    self.frame_count += 1
                else:
                    # If freenect fails, create a test pattern
                    self._create_test_pattern()
                
                # Get depth frame
                try:
                    depth_data = freenect.sync_get_depth()[0]
                    if depth_data is not None:
                        with self.lock:
                            self.depth_frame = depth_data
                except Exception as e:
                    print(f"Depth capture failed: {e}")
            else:
                # No freenect context, create test pattern
                self._create_test_pattern()
        except Exception as e:
            print(f"Error capturing freenect frames: {e}")
            # Fallback to test pattern
            self._create_test_pattern()'''
    
    # Fix 2: Add test pattern method
    test_pattern_method = '''
    def _create_test_pattern(self):
        """Create a test pattern when freenect fails"""
        import numpy as np
        import time
        
        # Create a test pattern with timestamp
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Add some color and text
        frame[100:200, 100:200] = [0, 255, 0]  # Green square
        frame[200:300, 200:300] = [255, 0, 0]  # Red square
        frame[300:400, 300:400] = [0, 0, 255]  # Blue square
        
        # Add timestamp
        timestamp = time.strftime("%H:%M:%S")
        cv2.putText(frame, f"TEST PATTERN - {timestamp}", (50, 50), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv2.putText(frame, "FREENECT CAPTURE FAILED", (50, 100), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
        
        with self.lock:
            self.frame = frame
        self.frame_count += 1'''
    
    # Apply the fixes
    if old_capture_method in content:
        content = content.replace(old_capture_method, new_capture_method)
        print("✅ Applied freenect capture fix")
    else:
        print("⚠️  Could not find old capture method - may already be fixed")
    
    # Add the test pattern method
    if "_create_test_pattern" not in content:
        # Find a good place to insert the method
        insert_point = content.find("    def _capture_opencv_frames(self):")
        if insert_point != -1:
            content = content[:insert_point] + test_pattern_method + "\n" + content[insert_point:]
            print("✅ Added test pattern method")
        else:
            print("⚠️  Could not find insertion point for test pattern method")
    
    # Write the fixed file
    with open("kinect_unified_streamer.py", "w") as f:
        f.write(content)
    
    print("✅ Freenect capture fix applied")
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
    print("🚀 Applying freenect capture fix...")
    
    # Change to the correct directory
    os.chdir("/home/ls/kinect_ws/src")
    
    # Apply the fix
    if apply_freenect_fix():
        # Restart the service
        restart_service()
        print("🎉 Freenect fix applied and service restarted!")
        print("The service should now show either real Kinect data or a test pattern.")
    else:
        print("❌ Fix could not be applied")
