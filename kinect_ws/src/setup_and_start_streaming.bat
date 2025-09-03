@echo off
echo Setup and Start Pi Streaming Service
echo ====================================

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Check if paramiko is available
python -c "import paramiko" >nul 2>&1
if errorlevel 1 (
    echo Installing paramiko...
    pip install paramiko
)

echo.
echo This will:
echo 1. Copy the streaming script to your Pi
echo 2. Start the Kinect streaming service
echo 3. Test the connection
echo.
echo Make sure your Pi is powered on and connected to the network.
echo.

python setup_and_start_streaming.py

echo.
echo Setup and start complete!
pause
