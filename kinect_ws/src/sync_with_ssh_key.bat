@echo off
title Sync to Pi with SSH Key
echo ========================================
echo   Sync to Pi with SSH Key Authentication
echo ========================================
echo.

REM Change to the script directory
cd /d "%~dp0"

echo Syncing files to Pi using SSH key authentication...
echo.

REM Get the SSH key path
set SSH_KEY_PATH=%USERPROFILE%\.ssh\pi_kinect_ls_192_168_1_9_key

echo Using SSH key: %SSH_KEY_PATH%
echo.

REM Check if SSH key exists
if not exist "%SSH_KEY_PATH%" (
    echo ERROR: SSH key not found at %SSH_KEY_PATH%
    echo Please run the SSH fix tool first: run_ssh_fix.bat
    echo.
    pause
    exit /b 1
)

echo Creating kinect_ws directory on Pi...
ssh -i "%SSH_KEY_PATH%" ls@192.168.1.9 "mkdir -p ~/kinect_ws"

echo.
echo Syncing camera streaming files...
scp -i "%SSH_KEY_PATH%" camera_streamer.py ls@192.168.1.9:~/kinect_ws/
scp -i "%SSH_KEY_PATH%" kinect_streamer.py ls@192.168.1.9:~/kinect_ws/
scp -i "%SSH_KEY_PATH%" kinect_unified_streamer.py ls@192.168.1.9:~/kinect_ws/
scp -i "%SSH_KEY_PATH%" kinect_launcher.py ls@192.168.1.9:~/kinect_ws/
scp -i "%SSH_KEY_PATH%" windows_camera_viewer.py ls@192.168.1.9:~/kinect_ws/
scp -i "%SSH_KEY_PATH%" requirements.txt ls@192.168.1.9:~/kinect_ws/

echo.
echo Making scripts executable...
ssh -i "%SSH_KEY_PATH%" ls@192.168.1.9 "chmod +x ~/kinect_ws/*.py"

echo.
echo ========================================
echo   Sync Complete
echo ========================================
echo.
echo Files synced to ~/kinect_ws/ on your Pi
echo.
echo To test the Kinect stream on your Pi:
echo 1. SSH into your Pi: ssh -i "%SSH_KEY_PATH%" ls@192.168.1.9
echo 2. Install dependencies: pip3 install -r ~/kinect_ws/requirements.txt
echo 3. Run unified Kinect stream: python3 ~/kinect_ws/kinect_unified_streamer.py
echo 4. Or use the launcher: python3 ~/kinect_ws/kinect_launcher.py
echo.
pause
