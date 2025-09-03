y@echo off
title Cleanup and Setup SSH Authentication
echo ========================================
echo   Cleanup and Setup SSH Authentication
echo ========================================
echo.

REM Change to the script directory
cd /d "%~dp0"

echo This will clean up old SSH keys and set up new ones for ls@192.168.1.9
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    pause
    exit /b 1
)

echo Step 1: Cleaning up old SSH keys...
if exist "%USERPROFILE%\.ssh\pi_kinect_key" (
    del "%USERPROFILE%\.ssh\pi_kinect_key"
    echo Deleted old private key
)
if exist "%USERPROFILE%\.ssh\pi_kinect_key.pub" (
    del "%USERPROFILE%\.ssh\pi_kinect_key.pub"
    echo Deleted old public key
)

echo.
echo Step 2: Setting up new SSH authentication for ls@192.168.1.9...
echo.

REM Run the SSH setup with correct username
python ssh_manager.py --pi-host 192.168.1.9 --pi-user ls --setup

echo.
echo Step 3: Testing the connection...
python ssh_manager.py --pi-host 192.168.1.9 --pi-user ls --test

echo.
echo ========================================
echo   SSH Authentication Setup Complete
echo ========================================
echo.
echo You can now connect using: ssh pi-kinect-ls
echo Or use the camera launcher without password prompts!
echo.
pause
