# PowerShell script to connect to Pi
Write-Host "Connecting to Pi..." -ForegroundColor Green
ssh -o PreferredAuthentications=password -o PubkeyAuthentication=no ls@192.168.1.9
