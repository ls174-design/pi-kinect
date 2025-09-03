@echo off
echo Robust Raspberry Pi Setup
echo =========================

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

REM Get Pi username
set /p PI_USER="Enter Pi username (default: pi): "
if "%PI_USER%"=="" set PI_USER=pi

REM Get Pi password
set /p PI_PASSWORD="Enter Pi password: "

echo.
echo Starting robust Pi setup...
echo This will:
echo 1. Test network connectivity
echo 2. Try multiple SSH authentication methods
echo 3. Deploy diagnostic tools to Pi
echo 4. Install all required libraries
echo 5. Run diagnostic check
echo.
echo This may take 15-20 minutes...
echo.

python robust_pi_setup.py --pi-host %PI_IP% --pi-user %PI_USER% --pi-password %PI_PASSWORD%

echo.
echo Setup complete!
pause
