@echo off
echo ========================================
echo Raspberry Pi Camera Streaming Setup
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.7+ and try again
    pause
    exit /b 1
)

echo Python found. Installing required packages...
pip install -r requirements.txt

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Make sure your Raspberry Pi is connected to the network
echo 2. Update the IP address in the scripts if needed (default: 192.168.1.9)
echo 3. Run the sync script to deploy to your Pi:
echo.
echo    python sync_to_pi.py --pi-host YOUR_PI_IP --install-deps --setup-service --start-service
echo.
echo 4. Open the camera viewer:
echo.
echo    python windows_camera_viewer.py
echo.
echo 5. Or open in browser: http://YOUR_PI_IP:8080
echo.
pause
