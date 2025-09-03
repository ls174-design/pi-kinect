@echo off
echo ========================================
echo   Create Desktop Shortcut
echo ========================================
echo.

REM Change to the script directory
cd /d "%~dp0"

echo Creating desktop shortcut for Camera System Launcher...
echo.

REM Check if PowerShell is available
powershell -Command "Get-Host" >nul 2>&1
if errorlevel 1 (
    echo Error: PowerShell is not available
    echo Please run this on a system with PowerShell installed
    pause
    exit /b 1
)

REM Run the PowerShell script to create the shortcut
powershell -ExecutionPolicy Bypass -File "create_desktop_shortcut.ps1"

echo.
echo Shortcut creation process completed.
pause
