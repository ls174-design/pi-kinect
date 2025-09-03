@echo off
echo ========================================
echo   Check Pi Files and Status
echo ========================================
echo.

set SSH_KEY=C:\Users\lysan\.ssh\pi_kinect_ls_192_168_1_9_key
set PI_HOST=192.168.1.9
set PI_USER=ls

echo Step 1: Testing network connectivity...
ping -n 3 %PI_HOST%
if %errorlevel% neq 0 (
    echo ❌ Pi is not responding to ping
    echo.
    echo Possible causes:
    echo - Pi lost WiFi connection
    echo - Pi got a new IP address
    echo - Pi crashed or rebooted
    echo - Network instability
    echo.
    echo Please check:
    echo 1. Pi's power LED (should be solid red)
    echo 2. Pi's network LED (should be blinking green)
    echo 3. Try running: .\find_pi_ip.bat
    echo.
    pause
    exit /b 1
)
echo ✅ Pi is responding to ping

echo.
echo Step 2: Testing SSH connection...
ssh -i "%SSH_KEY%" %PI_USER%@%PI_HOST% "echo 'SSH connection successful'"
if %errorlevel% neq 0 (
    echo ❌ SSH connection failed
    echo.
    echo Possible causes:
    echo - SSH service not running
    echo - Wrong SSH key
    echo - Pi username changed
    echo.
    pause
    exit /b 1
)
echo ✅ SSH connection successful

echo.
echo Step 3: Checking kinect_ws directory...
ssh -i "%SSH_KEY%" %PI_USER%@%PI_HOST% "ls -la ~/kinect_ws/"
if %errorlevel% neq 0 (
    echo ❌ kinect_ws directory not found
    echo.
    echo The directory might not have been created or files not transferred.
    echo Run: .\simple_deploy.bat
    echo.
    pause
    exit /b 1
)

echo.
echo Step 4: Checking individual files...
echo Checking camera_streamer.py...
ssh -i "%SSH_KEY%" %PI_USER%@%PI_HOST% "test -f ~/kinect_ws/camera_streamer.py && echo '✅ camera_streamer.py exists' || echo '❌ camera_streamer.py missing'"

echo Checking kinect_streamer.py...
ssh -i "%SSH_KEY%" %PI_USER%@%PI_HOST% "test -f ~/kinect_ws/kinect_streamer.py && echo '✅ kinect_streamer.py exists' || echo '❌ kinect_streamer.py missing'"

echo Checking requirements.txt...
ssh -i "%SSH_KEY%" %PI_USER%@%PI_HOST% "test -f ~/kinect_ws/requirements.txt && echo '✅ requirements.txt exists' || echo '❌ requirements.txt missing'"

echo.
echo Step 5: Checking Python dependencies...
ssh -i "%SSH_KEY%" %PI_USER%@%PI_HOST% "cd ~/kinect_ws && python3 -c 'import cv2, numpy, requests; print(\"✅ All dependencies installed\")' 2>/dev/null || echo '❌ Some dependencies missing - run: pip3 install -r requirements.txt'"

echo.
echo Step 6: Checking if camera stream is running...
ssh -i "%SSH_KEY%" %PI_USER%@%PI_HOST% "ps aux | grep camera_streamer | grep -v grep"
if %errorlevel% neq 0 (
    echo ❌ Camera stream is not running
    echo.
    echo To start the camera stream:
    echo   ssh -i "%SSH_KEY%" %PI_USER%@%PI_HOST%
    echo   cd ~/kinect_ws
    echo   python3 camera_streamer.py
    echo.
) else (
    echo ✅ Camera stream is running
)

echo.
echo Step 7: Checking port 8080...
ssh -i "%SSH_KEY%" %PI_USER%@%PI_HOST% "netstat -tuln | grep 8080"
if %errorlevel% neq 0 (
    echo ❌ Nothing listening on port 8080
) else (
    echo ✅ Port 8080 is active
)

echo.
echo ========================================
echo   Pi Status Check Complete
echo ========================================
echo.
pause
