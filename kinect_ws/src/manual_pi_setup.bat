@echo off
echo Manual Raspberry Pi Setup
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

echo.
echo This script will guide you through the Pi setup step by step.
echo It will test connectivity, upload files, and optionally install libraries.
echo.

python manual_pi_setup.py

echo.
echo Manual setup complete!
pause
