@echo off
echo Copying fixed files to Pi...
echo.
echo You will be prompted for the password for user 'ls' on 192.168.1.9
echo.

scp kinect_unified_streamer.py ls@192.168.1.9:~/kinect_ws/src/
if %errorlevel% equ 0 (
    echo.
    echo ✅ kinect_unified_streamer.py copied successfully!
    echo.
    echo Now copying the fix script...
    scp apply_streaming_fix.py ls@192.168.1.9:~/kinect_ws/src/
    if %errorlevel% equ 0 (
        echo.
        echo ✅ apply_streaming_fix.py copied successfully!
        echo.
        echo 🎉 All files copied! Now run this on the Pi:
        echo    cd /home/ls/kinect_ws/src
        echo    python3 apply_streaming_fix.py
    ) else (
        echo ❌ Failed to copy apply_streaming_fix.py
    )
) else (
    echo ❌ Failed to copy kinect_unified_streamer.py
)

pause
