# PowerShell script to copy updated pi-kinect files to Pi
Write-Host "Copying updated pi-kinect files to Pi..." -ForegroundColor Green
Write-Host ""
Write-Host "You will be prompted for the password for user 'ls' on 192.168.1.9" -ForegroundColor Yellow
Write-Host ""

try {
    # Create the directory on Pi first
    Write-Host "Creating directory on Pi..." -ForegroundColor Cyan
    ssh ls@192.168.1.9 "mkdir -p /home/ls/pi-kinect"
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Directory created successfully!" -ForegroundColor Green
        Write-Host ""
        
        # Copy all files
        Write-Host "Copying files to Pi..." -ForegroundColor Cyan
        scp -r . ls@192.168.1.9:/home/ls/pi-kinect/
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ All files copied successfully!" -ForegroundColor Green
            Write-Host ""
            
            # Make scripts executable
            Write-Host "Making scripts executable..." -ForegroundColor Cyan
            ssh ls@192.168.1.9 "cd /home/ls/pi-kinect && chmod +x setup/setup_pi_deps.sh scripts/v4l2_rgb_or_freenect.sh"
            
            if ($LASTEXITCODE -eq 0) {
                Write-Host "✅ Scripts made executable!" -ForegroundColor Green
                Write-Host ""
                Write-Host "🎉 Setup complete! Now you can run on the Pi:" -ForegroundColor Green
                Write-Host "   cd /home/ls/pi-kinect" -ForegroundColor White
                Write-Host "   ./setup/setup_pi_deps.sh" -ForegroundColor White
                Write-Host "   ./scripts/v4l2_rgb_or_freenect.sh 192.168.1.100" -ForegroundColor White
            } else {
                Write-Host "❌ Failed to make scripts executable" -ForegroundColor Red
            }
        } else {
            Write-Host "❌ Failed to copy files" -ForegroundColor Red
        }
    } else {
        Write-Host "❌ Failed to create directory on Pi" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Error during file transfer: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "Press any key to continue..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
