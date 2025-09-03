@echo off
echo Connecting to Pi...
ssh -o PreferredAuthentications=password -o PubkeyAuthentication=no ls@192.168.1.9
pause
