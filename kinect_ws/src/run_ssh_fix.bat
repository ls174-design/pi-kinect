@echo off
title SSH Authentication Fix
echo ========================================
echo    SSH Authentication Fix Tool
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

echo Python found. Running SSH Authentication Fix...
echo.

REM Check if the fix script exists
if not exist "fix_ssh_auth.py" (
    echo Error: fix_ssh_auth.py not found in current directory
    echo Current directory: %CD%
    echo.
    pause
    exit /b 1
)

REM Run the SSH fix
python fix_ssh_auth.py

REM If we get here, the fix has completed
echo.
echo SSH Authentication Fix completed.
pause
