# Camera System Shortcut Setup

This guide explains how to set up one-click shortcuts to launch your camera system (both PC viewer and Pi camera stream).

## Quick Setup (Recommended)

### Option 1: Automatic Shortcut Creation
1. **Run the shortcut creator:**
   ```cmd
   create_shortcut.bat
   ```
   This will create a desktop shortcut automatically.

### Option 2: Manual Setup
1. **Create a desktop shortcut manually:**
   - Right-click on your desktop
   - Select "New" → "Shortcut"
   - Browse to and select `start_camera_system.bat`
   - Name it "Camera System Launcher"
   - Click "Finish"

## What the Shortcut Does

When you double-click the shortcut, it will:

1. **Launch the Camera System Launcher GUI** - A user-friendly interface
2. **Test Pi Connection** - Verify your Raspberry Pi is reachable
3. **Start PC Camera Viewer** - Opens the Windows camera viewer application
4. **Open Pi Stream in Browser** - Automatically opens the Pi camera stream in your default browser
5. **Provide Status Updates** - Shows real-time status of all components

## Configuration

### Before First Use
1. **Update Pi IP Address:**
   - Open the launcher
   - Change the "Raspberry Pi IP" field to match your Pi's IP address
   - Default is `192.168.1.9`

2. **Ensure Pi Camera Stream is Running:**
   - Make sure `camera_streamer.py` is running on your Raspberry Pi
   - Or set up the service to start automatically

### Pi Setup (if not already done)
```bash
# On your Raspberry Pi, run:
python3 camera_streamer.py
```

Or set up as a service:
```bash
# Deploy and start service
python sync_to_pi.py --pi-host YOUR_PI_IP --install-deps --setup-service --start-service
```

## Files Created

- `launch_camera_system.py` - Main launcher application with GUI
- `start_camera_system.bat` - Batch file to start the launcher
- `create_desktop_shortcut.ps1` - PowerShell script to create shortcuts
- `create_shortcut.bat` - Batch file to run the shortcut creator

## Features

### Camera System Launcher GUI
- **One-click launch** of entire camera system
- **Connection testing** to verify Pi connectivity
- **Status monitoring** with real-time updates
- **Quick access buttons** for individual components
- **Configuration panel** for Pi IP and port settings

### Quick Access Options
- **Launch Camera System** - Starts everything at once
- **Open Pi Stream in Browser** - Direct browser access to Pi camera
- **Open PC Viewer Only** - Just the Windows camera viewer
- **Test Pi Connection** - Verify connectivity before launching

## Troubleshooting

### Common Issues

1. **"Python not found" error:**
   - Install Python 3.7+ and ensure it's in your PATH
   - Or use the full path to python.exe in the batch file

2. **"Pi connection failed":**
   - Check that your Pi is on the same network
   - Verify the IP address is correct
   - Ensure `camera_streamer.py` is running on the Pi

3. **"PC viewer won't start":**
   - Check that all required Python packages are installed
   - Run `pip install -r requirements.txt`

4. **Shortcut creation fails:**
   - Run as Administrator if needed
   - Check that PowerShell execution policy allows scripts

### Manual Launch Commands

If shortcuts don't work, you can launch manually:

```cmd
# Start the launcher GUI
python launch_camera_system.py

# Or start components individually
python windows_camera_viewer.py
```

## Advanced Configuration

### Custom Pi IP
Edit `launch_camera_system.py` and change the default IP:
```python
self.pi_ip = tk.StringVar(value="YOUR_PI_IP_HERE")
```

### Custom Port
Change the default port if needed:
```python
self.pi_port = tk.StringVar(value="8080")
```

### Auto-start on Windows Boot
1. Copy the shortcut to your Startup folder:
   - Press `Win + R`, type `shell:startup`
   - Copy your shortcut to this folder

## Support

If you encounter issues:
1. Check the status messages in the launcher GUI
2. Verify all components are properly installed
3. Test individual components separately
4. Check network connectivity between PC and Pi

## File Structure
```
kinect_ws/src/
├── launch_camera_system.py      # Main launcher GUI
├── start_camera_system.bat      # Batch launcher
├── create_desktop_shortcut.ps1  # Shortcut creator
├── create_shortcut.bat          # Shortcut creator runner
├── windows_camera_viewer.py     # PC camera viewer
├── camera_streamer.py           # Pi camera streamer
└── SHORTCUT_SETUP.md           # This guide
```
