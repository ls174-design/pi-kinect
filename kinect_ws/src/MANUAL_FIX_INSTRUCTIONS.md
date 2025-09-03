# Manual Fix Instructions for Pi Streaming Issue

## Problem Identified
The camera viewer shows "KINECT READY - FREENECT_SYST" status frame instead of real camera data because of a bug in the `kinect_unified_streamer.py` file.

## Root Cause
- The `kinect_method` is set to `'freenect_system'` 
- But the `capture_frames()` method only checks for `'freenect'` and `'opencv'`
- Since `'freenect_system'` doesn't match, it falls through to show status frames

## Manual Fix Steps

### Option 1: Use the Fix Script (Recommended)
1. Copy `apply_streaming_fix.py` to the Pi (via USB, email, or other means)
2. On the Pi, run:
   ```bash
   cd /home/ls/kinect_ws/src
   python3 apply_streaming_fix.py
   ```

### Option 2: Manual Edit
1. On the Pi, edit the file:
   ```bash
   nano /home/ls/kinect_ws/src/kinect_unified_streamer.py
   ```

2. Find line 208 (around the `capture_frames` method)
3. Change this line:
   ```python
   if self.kinect_method == 'freenect':
   ```
   To this:
   ```python
   if self.kinect_method in ['freenect', 'freenect_system']:
   ```

4. Save the file (Ctrl+X, Y, Enter in nano)

5. Restart the service:
   ```bash
   pkill -f kinect_unified_streamer
   python3 kinect_unified_streamer.py --host 0.0.0.0 --port 8080 &
   ```

## Verification
After applying the fix:
1. The camera viewer should show real camera data instead of status frames
2. Run the diagnostic: `python3 diagnose_streaming_issue.py 192.168.1.9`
3. The `/stream` endpoint should return real image data

## Files Modified
- `kinect_unified_streamer.py` - Fixed kinect_method detection logic

## Expected Result
- Camera viewer will display actual Kinect camera feed
- Status will show "Camera available: True" instead of "Unknown"
- Real-time video streaming will work properly
