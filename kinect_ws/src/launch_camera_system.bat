@echo off
echo Camera System Launcher
echo ======================

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    pause
    exit /b 1
)

echo.
echo This will launch the comprehensive camera system launcher.
echo It will help you:
echo - Check Pi connectivity
echo - Start the streaming service
echo - Open the camera viewer
echo.

python launch_camera_system.py

echo.
echo Camera system launcher closed.
pause
