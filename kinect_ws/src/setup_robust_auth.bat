@echo off
title Setup Robust SSH Authentication
echo ========================================
echo   Setup Robust SSH Authentication
echo ========================================
echo.

REM Change to the script directory
cd /d "%~dp0"

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.7+ and try again
    echo.
    pause
    exit /b 1
)

echo Python found. Setting up robust SSH authentication...
echo.

REM Get Pi IP from user
set /p PI_IP="Enter Raspberry Pi IP address (default: 192.168.1.9): "
if "%PI_IP%"=="" set PI_IP=192.168.1.9

REM Get Pi username from user
set /p PI_USER="Enter Raspberry Pi username (default: ls): "
if "%PI_USER%"=="" set PI_USER=ls

echo.
echo Setting up SSH authentication for %PI_USER%@%PI_IP%...
echo This will eliminate password prompts for future connections.
echo.

REM Run the SSH setup
python ssh_manager.py --pi-host %PI_IP% --pi-user %PI_USER% --setup

echo.
echo ========================================
echo   SSH Authentication Setup Complete
echo ========================================
echo.
echo Your Pi connection is now configured for passwordless access!
echo.
echo Next steps:
echo 1. Test the connection: python ssh_manager.py --pi-host %PI_IP% --pi-user %PI_USER% --test
echo 2. Use the robust sync: python robust_sync_to_pi.py --pi-host %PI_IP% --pi-user %PI_USER% --setup-auth
echo 3. Launch the camera system: start_camera_system.bat
echo.
pause
