@echo off
title Quick Sync to Pi
echo ========================================
echo   Quick Sync to Pi
echo ========================================
echo.

REM Change to the script directory
cd /d "%~dp0"

echo Syncing essential camera files to your Pi...
echo You will need to enter your Pi password when prompted
echo.

echo Creating kinect_ws directory on Pi...
ssh ls@192.168.1.9 "mkdir -p ~/kinect_ws"

echo.
echo Syncing camera streaming files...
scp camera_streamer.py ls@192.168.1.9:~/kinect_ws/
scp kinect_streamer.py ls@192.168.1.9:~/kinect_ws/
scp kinect_unified_streamer.py ls@192.168.1.9:~/kinect_ws/
scp kinect_launcher.py ls@192.168.1.9:~/kinect_ws/
scp windows_camera_viewer.py ls@192.168.1.9:~/kinect_ws/
scp requirements.txt ls@192.168.1.9:~/kinect_ws/

echo.
echo Making scripts executable...
ssh ls@192.168.1.9 "chmod +x ~/kinect_ws/*.py"

echo.
echo ========================================
echo   Quick Sync Complete
echo ========================================
echo.
echo Essential files synced to ~/kinect_ws/ on your Pi
echo.
echo To test the Kinect stream on your Pi:
echo 1. SSH into your Pi: ssh ls@192.168.1.9
echo 2. Install dependencies: pip3 install -r ~/kinect_ws/requirements.txt
echo 3. Run unified Kinect stream: python3 ~/kinect_ws/kinect_unified_streamer.py
echo 4. Or use the launcher: python3 ~/kinect_ws/kinect_launcher.py
echo.
pause
