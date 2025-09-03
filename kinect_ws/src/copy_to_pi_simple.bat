@echo off
echo Copy Setup Files to Raspberry Pi
echo ================================

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
echo This will copy the Linux setup files to your Pi.
echo.

python copy_to_pi_simple.py

echo.
echo File copy complete!
pause
