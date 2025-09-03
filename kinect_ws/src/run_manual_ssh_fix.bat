@echo off
title Manual SSH Fix
echo ========================================
echo   Manual SSH Authentication Fix
echo ========================================
echo.

REM Change to the script directory
cd /d "%~dp0"

echo This will manually fix the SSH authentication issue
echo.

python manual_ssh_fix.py

echo.
echo Manual SSH fix completed.
pause
