# PowerShell script to copy files to Pi
Write-Host "Copying fixed files to Pi..." -ForegroundColor Green
Write-Host ""
Write-Host "You will be prompted for the password for user 'ls' on 192.168.1.9" -ForegroundColor Yellow
Write-Host ""

try {
    # Copy the fixed unified streamer
    Write-Host "Copying kinect_unified_streamer.py..." -ForegroundColor Cyan
    scp kinect_unified_streamer.py ls@192.168.1.9:~/kinect_ws/src/
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ kinect_unified_streamer.py copied successfully!" -ForegroundColor Green
        Write-Host ""
        
        # Copy the fix script
        Write-Host "Copying apply_streaming_fix.py..." -ForegroundColor Cyan
        scp apply_streaming_fix.py ls@192.168.1.9:~/kinect_ws/src/
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ apply_streaming_fix.py copied successfully!" -ForegroundColor Green
            Write-Host ""
            Write-Host "🎉 All files copied! Now run this on the Pi:" -ForegroundColor Green
            Write-Host "   cd /home/ls/kinect_ws/src" -ForegroundColor White
            Write-Host "   python3 apply_streaming_fix.py" -ForegroundColor White
        } else {
            Write-Host "❌ Failed to copy apply_streaming_fix.py" -ForegroundColor Red
        }
    } else {
        Write-Host "❌ Failed to copy kinect_unified_streamer.py" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Error during file transfer: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "Press any key to continue..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
