@echo off
echo SSH Troubleshooting Tool for Raspberry Pi
echo =========================================

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
echo Testing SSH connection to %PI_USER%@%PI_IP%...
echo.

python ssh_troubleshoot.py --pi-host %PI_IP% --pi-user %PI_USER% --pi-password %PI_PASSWORD%

echo.
echo Troubleshooting complete!
pause
