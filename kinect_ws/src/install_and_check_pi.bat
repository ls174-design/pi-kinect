@echo off
echo Installing and Checking Libraries on Raspberry Pi
echo ================================================

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

REM Get Pi IP address
set /p PI_IP="Enter Raspberry Pi IP address: "

REM Get Pi password
set /p PI_PASSWORD="Enter Pi password: "

echo.
echo Installing libraries on Pi at %PI_IP%...
echo This may take several minutes...
echo.

python run_pi_diagnostic.py --pi-host %PI_IP% --pi-password %PI_PASSWORD% --install --check-service

echo.
echo Installation and diagnostic complete!
echo.
echo Next steps:
echo 1. Connect your Kinect to the Pi
echo 2. Run: python kinect_unified_streamer.py on the Pi
echo 3. Open http://%PI_IP%:8080 in your browser
echo.
pause
