@echo off
title Deploy Camera Code to Pi
echo ========================================
echo   Deploy Camera Code to Pi
echo ========================================
echo.

REM Change to the script directory
cd /d "%~dp0"

echo This will deploy the camera streaming code to your Pi
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    pause
    exit /b 1
)

echo Step 1: Testing SSH connection...
python ssh_manager.py --pi-host 192.168.1.9 --pi-user ls --test
if errorlevel 1 (
    echo SSH authentication failed. Please run fix_ssh_auth.bat first.
    pause
    exit /b 1
)

echo.
echo Step 2: Deploying camera streaming files...
python robust_sync_to_pi.py --pi-host 192.168.1.9 --pi-user ls --sync-files

echo.
echo Step 3: Installing dependencies...
python robust_sync_to_pi.py --pi-host 192.168.1.9 --pi-user ls --install-deps

echo.
echo Step 4: Setting up camera service...
python robust_sync_to_pi.py --pi-host 192.168.1.9 --pi-user ls --setup-service

echo.
echo Step 5: Starting camera service...
python robust_sync_to_pi.py --pi-host 192.168.1.9 --pi-user ls --start-service

echo.
echo Step 6: Testing camera stream...
python robust_sync_to_pi.py --pi-host 192.168.1.9 --pi-user ls --test-stream

echo.
echo ========================================
echo   Camera Deployment Complete
echo ========================================
echo.
echo Your camera stream should now be available at:
echo http://192.168.1.9:8080
echo.
pause
