@echo off
title Smart Sync to Pi
echo ========================================
echo   Smart Sync to Pi
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

echo Python found. Running Smart Sync...
echo.

REM Check if the sync script exists
if not exist "smart_sync.py" (
    echo Error: smart_sync.py not found in current directory
    echo Current directory: %CD%
    echo.
    pause
    exit /b 1
)

REM Run the smart sync
python smart_sync.py

REM If we get here, the sync has completed
echo.
echo Smart Sync completed.
pause
