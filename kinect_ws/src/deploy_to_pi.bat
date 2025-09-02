@echo off
echo ========================================
echo Deploy Camera Streaming to Raspberry Pi
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    pause
    exit /b 1
)

echo Python found. Starting deployment...
echo.

REM Get Pi IP from user
set /p PI_IP="Enter Raspberry Pi IP address (default: 192.168.1.9): "
if "%PI_IP%"=="" set PI_IP=192.168.1.9

echo.
echo Deploying to Raspberry Pi at %PI_IP%...
echo.

REM Run the sync script with all options
python sync_to_pi.py --pi-host %PI_IP% --pi-user pi --install-deps --setup-service --start-service

echo.
echo ========================================
echo Deployment Complete!
echo ========================================
echo.
echo Your camera stream should now be available at:
echo http://%PI_IP%:8080
echo.
echo You can also run the Windows viewer:
echo python windows_camera_viewer.py
echo.
pause
