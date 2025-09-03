@echo off
echo Complete Raspberry Pi Setup
echo ===========================

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
echo Starting complete Pi setup...
echo This will:
echo 1. Deploy diagnostic tools to Pi
echo 2. Install all required libraries
echo 3. Run diagnostic check
echo 4. Check streaming service status
echo.
echo This may take 15-20 minutes...
echo.

python full_pi_setup.py --pi-host %PI_IP% --pi-password %PI_PASSWORD%

echo.
echo Setup complete!
pause
