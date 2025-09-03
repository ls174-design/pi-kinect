@echo off
title Fix SSH Authentication for ls@192.168.1.9
echo ========================================
echo   Fix SSH Authentication
echo ========================================
echo.

REM Change to the script directory
cd /d "%~dp0"

echo This will clean up old SSH keys and set up new ones for ls@192.168.1.9
echo.

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
echo Step 2: Setting up new SSH authentication...
python ssh_manager.py --pi-host 192.168.1.9 --pi-user ls --setup

echo.
echo Step 3: Testing the connection...
python ssh_manager.py --pi-host 192.168.1.9 --pi-user ls --test

echo.
echo ========================================
echo   SSH Authentication Fix Complete
echo ========================================
echo.
echo You can now connect using: ssh pi-kinect-ls
echo Or use the camera launcher without password prompts!
echo.
pause
