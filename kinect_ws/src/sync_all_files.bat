@echo off
title Sync All Files to Pi
echo ========================================
echo   Sync All Files to Pi
echo ========================================
echo.

REM Change to the script directory
cd /d "%~dp0"

echo This will sync all camera system files to your Pi
echo You will need to enter your Pi password when prompted
echo.

echo Files to sync:
echo - camera_streamer.py
echo - kinect_streamer.py
echo - windows_camera_viewer.py
echo - ssh_manager.py
echo - robust_sync_to_pi.py
echo - launch_camera_system.py
echo - manual_ssh_fix.py
echo - requirements.txt
echo.

pause

echo Step 1: Syncing core camera files...
scp camera_streamer.py ls@192.168.1.9:~/kinect_ws/
scp kinect_streamer.py ls@192.168.1.9:~/kinect_ws/
scp windows_camera_viewer.py ls@192.168.1.9:~/kinect_ws/
scp requirements.txt ls@192.168.1.9:~/kinect_ws/

echo.
echo Step 2: Syncing SSH management files...
scp ssh_manager.py ls@192.168.1.9:~/kinect_ws/
scp robust_sync_to_pi.py ls@192.168.1.9:~/kinect_ws/
scp manual_ssh_fix.py ls@192.168.1.9:~/kinect_ws/

echo.
echo Step 3: Syncing launcher files...
scp launch_camera_system.py ls@192.168.1.9:~/kinect_ws/
scp start_camera_system.bat ls@192.168.1.9:~/kinect_ws/

echo.
echo Step 4: Making scripts executable...
ssh ls@192.168.1.9 "chmod +x ~/kinect_ws/*.py"

echo.
echo ========================================
echo   File Sync Complete
echo ========================================
echo.
echo All files have been synced to your Pi at ~/kinect_ws/
echo.
echo Next steps:
echo 1. SSH into your Pi: ssh ls@192.168.1.9
echo 2. Install dependencies: pip3 install -r ~/kinect_ws/requirements.txt
echo 3. Test camera stream: python3 ~/kinect_ws/camera_streamer.py
echo.
pause
