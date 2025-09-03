@echo off
echo ========================================
echo   Simple Camera Deployment to Pi
echo ========================================
echo.

set SSH_KEY=C:\Users\lysan\.ssh\pi_kinect_ls_192_168_1_9_key
set PI_HOST=192.168.1.9
set PI_USER=ls

echo Step 1: Testing SSH connection...
ssh -i "%SSH_KEY%" -o ConnectTimeout=10 -o StrictHostKeyChecking=no %PI_USER%@%PI_HOST% "echo 'SSH connection successful'"
if %errorlevel% neq 0 (
    echo ❌ SSH connection failed
    pause
    exit /b 1
)
echo ✅ SSH connection successful

echo.
echo Step 2: Creating kinect_ws directory on Pi...
ssh -i "%SSH_KEY%" -o ConnectTimeout=10 -o StrictHostKeyChecking=no %PI_USER%@%PI_HOST% "mkdir -p ~/kinect_ws"

echo.
echo Step 3: Copying camera streaming files...
scp -i "%SSH_KEY%" camera_streamer.py %PI_USER%@%PI_HOST%:~/kinect_ws/
scp -i "%SSH_KEY%" kinect_streamer.py %PI_USER%@%PI_HOST%:~/kinect_ws/
scp -i "%SSH_KEY%" requirements.txt %PI_USER%@%PI_HOST%:~/kinect_ws/

echo.
echo Step 4: Making scripts executable...
ssh -i "%SSH_KEY%" -o ConnectTimeout=10 -o StrictHostKeyChecking=no %PI_USER%@%PI_HOST% "chmod +x ~/kinect_ws/*.py"

echo.
echo Step 5: Installing Python dependencies...
ssh -i "%SSH_KEY%" -o ConnectTimeout=10 -o StrictHostKeyChecking=no %PI_USER%@%PI_HOST% "cd ~/kinect_ws && pip3 install -r requirements.txt"

echo.
echo ========================================
echo   Deployment Complete!
echo ========================================
echo.
echo To start the camera stream on your Pi:
echo   ssh -i "%SSH_KEY%" %PI_USER%@%PI_HOST%
echo   cd ~/kinect_ws
echo   python3 camera_streamer.py
echo.
echo To view the stream from your PC:
echo   python windows_camera_viewer.py
echo.
pause
