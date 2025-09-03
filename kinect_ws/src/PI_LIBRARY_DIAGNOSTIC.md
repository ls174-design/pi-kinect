# Raspberry Pi Library Diagnostic Tools

This directory contains comprehensive tools to check and install all required libraries for Kinect streaming on your Raspberry Pi.

## The Problem

You're getting HTTP 503 errors when trying to connect to your Pi's streaming service. This typically means:

1. **Missing libraries** - freenect, OpenCV, or other dependencies not installed
2. **Service not running** - The streaming service isn't started on the Pi
3. **Hardware issues** - Kinect not properly connected or recognized

## Quick Solution

### Option 1: Run Quick Check (Windows)
```bash
# Double-click this file or run in command prompt:
quick_pi_check.bat
```

### Option 2: Manual Installation
```bash
# Run this on your Pi:
bash install_pi_libraries.sh
```

## Diagnostic Tools

### 1. `check_pi_libraries.py`
**Purpose**: Comprehensive library check that runs directly on the Pi
**What it checks**:
- ✅ Python modules (OpenCV, NumPy, freenect, etc.)
- ✅ System libraries (libfreenect, libopencv)
- ✅ Kinect hardware detection
- ✅ USB device enumeration
- ✅ Video device availability
- ✅ Network port status

**Usage**:
```bash
# On the Pi:
python3 check_pi_libraries.py
```

### 2. `run_pi_diagnostic.py`
**Purpose**: Remote diagnostic tool that connects to your Pi from Windows
**Features**:
- 🔌 SSH connection to Pi
- 📤 Uploads diagnostic script to Pi
- 🚀 Runs comprehensive checks remotely
- 📥 Downloads results back to Windows

**Usage**:
```bash
# From Windows:
python run_pi_diagnostic.py --pi-host 192.168.1.100 --pi-password your_password
```

### 3. `install_pi_libraries.sh`
**Purpose**: Automated installation script for all required libraries
**What it installs**:
- 📦 System dependencies (cmake, libusb, etc.)
- 📦 OpenCV system libraries
- 📦 freenect system libraries
- 🐍 Python packages (opencv-python, numpy, freenect, etc.)
- 🔄 Updates library cache

**Usage**:
```bash
# On the Pi:
bash install_pi_libraries.sh
```

## Windows Batch Files

### `quick_pi_check.bat`
- Simple interface to run diagnostic
- Prompts for Pi IP address
- Tries SSH key first, then password

### `run_pi_diagnostic.bat`
- Runs diagnostic with service check
- Prompts for Pi IP and password

### `install_and_check_pi.bat`
- Installs libraries AND runs diagnostic
- Complete setup in one go

## Expected Results

### ✅ All Libraries Installed
```
✅ OpenCV: Available
✅ NumPy: Available  
✅ Freenect: Available
✅ libfreenect found: /usr/local/lib/libfreenect.so
✅ Kinect device detected in USB devices
✅ Freenect devices found: 1
```

### ❌ Missing Libraries
```
❌ Freenect: Missing - No module named 'freenect'
❌ libfreenect system library not found
❌ No Kinect device found in USB devices
```

## Troubleshooting

### HTTP 503 Error
This means the streaming service isn't running. Check:

1. **Libraries installed?**
   ```bash
   python3 check_pi_libraries.py
   ```

2. **Service running?**
   ```bash
   # On Pi:
   python3 kinect_unified_streamer.py
   ```

3. **Port available?**
   ```bash
   # On Pi:
   netstat -tuln | grep 8080
   ```

### Missing freenect Library
```bash
# Install on Pi:
sudo apt-get install -y libfreenect-dev python3-freenect
pip3 install freenect
```

### Missing OpenCV
```bash
# Install on Pi:
sudo apt-get install -y python3-opencv libopencv-dev
pip3 install opencv-python
```

### Kinect Not Detected
1. **Check USB connection**
   ```bash
   lsusb | grep -i microsoft
   ```

2. **Check video devices**
   ```bash
   ls /dev/video*
   ```

3. **Test freenect**
   ```bash
   python3 -c "import freenect; print('Devices:', freenect.num_devices(freenect.init()))"
   ```

## Step-by-Step Fix

1. **Run diagnostic**:
   ```bash
   # From Windows:
   quick_pi_check.bat
   ```

2. **Install missing libraries**:
   ```bash
   # On Pi:
   bash install_pi_libraries.sh
   ```

3. **Verify installation**:
   ```bash
   # On Pi:
   python3 check_pi_libraries.py
   ```

4. **Start streaming service**:
   ```bash
   # On Pi:
   python3 kinect_unified_streamer.py
   ```

5. **Test connection**:
   ```bash
   # From Windows browser:
   http://YOUR_PI_IP:8080
   ```

## Common Issues

### "No module named 'freenect'"
- Run: `bash install_pi_libraries.sh`
- Or: `pip3 install freenect`

### "libfreenect.so not found"
- Run: `sudo apt-get install -y libfreenect-dev`
- Then: `sudo ldconfig`

### "No Kinect devices found"
- Check USB connection
- Try different USB port
- Check power supply (Kinect needs external power)

### "Port 8080 already in use"
- Kill existing process: `sudo pkill -f kinect`
- Or use different port: `python3 kinect_unified_streamer.py --port 8081`

## Support

If you're still having issues:

1. Run the full diagnostic: `python run_pi_diagnostic.py --pi-host YOUR_PI_IP --install`
2. Check the output for specific error messages
3. Verify your Kinect is properly connected and powered
4. Make sure your Pi has internet access for package downloads
