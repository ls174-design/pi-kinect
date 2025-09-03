@echo off
title Network Diagnostic for Pi Connection
echo ========================================
echo   Network Diagnostic for Pi Connection
echo ========================================
echo.

echo Checking network connectivity to Pi at 192.168.1.9...
echo.

echo Step 1: Checking ARP table for Pi...
arp -a | findstr "192.168.1.9"
if errorlevel 1 (
    echo ❌ Pi not found in ARP table
) else (
    echo ✅ Pi found in ARP table
)

echo.
echo Step 2: Testing basic connectivity...
ping -n 4 192.168.1.9
if errorlevel 1 (
    echo ❌ Pi is not responding to pings
) else (
    echo ✅ Pi is responding to pings
)

echo.
echo Step 3: Testing SSH port...
powershell "Test-NetConnection -ComputerName 192.168.1.9 -Port 22 -InformationLevel Quiet"
if errorlevel 1 (
    echo ❌ SSH port 22 is not accessible
) else (
    echo ✅ SSH port 22 is accessible
)

echo.
echo Step 4: Checking your network configuration...
echo Your PC IP: 
ipconfig | findstr "IPv4 Address" | findstr "192.168.1"

echo.
echo ========================================
echo   Diagnostic Complete
echo ========================================
echo.
echo If Pi is not responding:
echo 1. Check if Pi is powered on
echo 2. Check if Pi is connected to WiFi
echo 3. Try accessing Pi directly with monitor/keyboard
echo 4. Check if Pi's IP address changed
echo.
pause
