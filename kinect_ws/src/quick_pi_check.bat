@echo off
echo Quick Raspberry Pi Library Check
echo ================================

REM Get Pi IP address
set /p PI_IP="Enter Raspberry Pi IP address (e.g., 192.168.1.100): "

echo.
echo Checking libraries on Pi at %PI_IP%...
echo.

REM Try to run diagnostic without password first (SSH key)
echo Attempting connection with SSH key...
python run_pi_diagnostic.py --pi-host %PI_IP% --check-service

if errorlevel 1 (
    echo.
    echo SSH key authentication failed. Trying with password...
    set /p PI_PASSWORD="Enter Pi password: "
    python run_pi_diagnostic.py --pi-host %PI_IP% --pi-password %PI_PASSWORD% --check-service
)

echo.
echo Check complete!
pause
