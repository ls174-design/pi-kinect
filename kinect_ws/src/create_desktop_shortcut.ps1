# PowerShell script to create a desktop shortcut for the Camera System Launcher
# Run this script as Administrator if needed

param(
    [string]$ShortcutName = "Camera System Launcher",
    [string]$TargetPath = "",
    [string]$IconPath = ""
)

# Get the directory where this script is located
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Set default paths if not provided
if ($TargetPath -eq "") {
    $TargetPath = Join-Path $ScriptDir "start_camera_system.bat"
}

if ($IconPath -eq "") {
    # Use a default camera icon or the batch file icon
    $IconPath = "shell32.dll,14"  # Camera icon from Windows shell32.dll
}

# Get the desktop path
$DesktopPath = [Environment]::GetFolderPath("Desktop")
$ShortcutPath = Join-Path $DesktopPath "$ShortcutName.lnk"

Write-Host "Creating desktop shortcut..." -ForegroundColor Green
Write-Host "Target: $TargetPath" -ForegroundColor Yellow
Write-Host "Shortcut: $ShortcutPath" -ForegroundColor Yellow

try {
    # Create the shortcut
    $WshShell = New-Object -comObject WScript.Shell
    $Shortcut = $WshShell.CreateShortcut($ShortcutPath)
    $Shortcut.TargetPath = $TargetPath
    $Shortcut.WorkingDirectory = $ScriptDir
    $Shortcut.Description = "Launch Camera System - PC Viewer and Pi Camera Stream"
    $Shortcut.IconLocation = $IconPath
    $Shortcut.Save()
    
    Write-Host "✅ Desktop shortcut created successfully!" -ForegroundColor Green
    Write-Host "Shortcut location: $ShortcutPath" -ForegroundColor Cyan
    
    # Ask if user wants to create a Start Menu shortcut as well
    $CreateStartMenu = Read-Host "`nWould you like to create a Start Menu shortcut as well? (y/n)"
    if ($CreateStartMenu -eq "y" -or $CreateStartMenu -eq "Y") {
        $StartMenuPath = [Environment]::GetFolderPath("StartMenu")
        $StartMenuShortcutPath = Join-Path $StartMenuPath "$ShortcutName.lnk"
        
        $StartMenuShortcut = $WshShell.CreateShortcut($StartMenuShortcutPath)
        $StartMenuShortcut.TargetPath = $TargetPath
        $StartMenuShortcut.WorkingDirectory = $ScriptDir
        $StartMenuShortcut.Description = "Launch Camera System - PC Viewer and Pi Camera Stream"
        $StartMenuShortcut.IconLocation = $IconPath
        $StartMenuShortcut.Save()
        
        Write-Host "✅ Start Menu shortcut created successfully!" -ForegroundColor Green
        Write-Host "Start Menu shortcut location: $StartMenuShortcutPath" -ForegroundColor Cyan
    }
    
} catch {
    Write-Host "❌ Error creating shortcut: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Make sure you have permission to write to the Desktop folder." -ForegroundColor Yellow
}

Write-Host "`nPress any key to continue..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
