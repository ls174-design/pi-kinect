@echo off
title Kinect Diagnostic Tool
echo ========================================
echo    Kinect Diagnostic Tool
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

echo Python found. Running Kinect Diagnostic...
echo.

REM Check if the diagnostic script exists
if not exist "kinect_diagnostic.py" (
    echo Error: kinect_diagnostic.py not found in current directory
    echo Current directory: %CD%
    echo.
    pause
    exit /b 1
)

REM Run the diagnostic
python kinect_diagnostic.py

REM If we get here, the diagnostic has completed
echo.
echo Diagnostic completed.
pause
