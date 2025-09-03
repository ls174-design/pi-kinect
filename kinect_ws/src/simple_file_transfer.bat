@echo off
echo Simple File Transfer to Raspberry Pi
echo ====================================

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
echo This will simply upload the diagnostic files to your Pi.
echo.

python simple_file_transfer.py

echo.
echo File transfer complete!
pause
