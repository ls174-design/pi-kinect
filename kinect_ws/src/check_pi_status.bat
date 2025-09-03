@echo off
echo Pi Status Checker
echo =================

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Check if requests is available
python -c "import requests" >nul 2>&1
if errorlevel 1 (
    echo Installing requests...
    pip install requests
)

echo.
echo This will check if your Pi is online and if the streaming service is running.
echo.

python check_pi_status.py

echo.
echo Status check complete!
pause
