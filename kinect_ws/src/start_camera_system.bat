@echo off
title Camera System Launcher
echo ========================================
echo    Camera System Launcher
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

echo Python found. Starting Camera System Launcher...
echo.

REM Check if the launcher script exists
if not exist "launch_camera_system.py" (
    echo Error: launch_camera_system.py not found in current directory
    echo Current directory: %CD%
    echo.
    pause
    exit /b 1
)

REM Start the launcher
python launch_camera_system.py

REM If we get here, the launcher has closed
echo.
echo Camera System Launcher has closed.
pause
