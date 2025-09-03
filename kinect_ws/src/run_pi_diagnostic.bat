@echo off
echo Running Raspberry Pi Library Diagnostic
echo ======================================

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
set /p PI_PASSWORD="Enter Pi password (or press Enter to skip): "

echo.
echo Running diagnostic on Pi at %PI_IP%...
echo.

if "%PI_PASSWORD%"=="" (
    python run_pi_diagnostic.py --pi-host %PI_IP% --check-service
) else (
    python run_pi_diagnostic.py --pi-host %PI_IP% --pi-password %PI_PASSWORD% --check-service
)

echo.
echo Diagnostic complete!
pause