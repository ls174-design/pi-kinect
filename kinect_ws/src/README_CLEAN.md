# Raspberry Pi Kinect Streaming - Clean Codebase

This is the cleaned and organized codebase for streaming Kinect camera feeds from a Raspberry Pi to a Windows laptop.

## 🎯 Quick Start

### 1. Setup Raspberry Pi
```bash
# Copy setup files to Pi
copy_to_pi_simple.bat

# SSH to Pi and run complete setup
ssh ls@192.168.1.9
cd kinect_setup
bash complete_pi_setup.sh
```

### 2. Start Streaming Service
```bash
# Complete setup and start streaming
setup_and_start_streaming.bat
```

### 3. View Camera Feed
```bash
# Launch camera viewer
launch_working_camera_viewer.bat
```

## 📁 Essential Files

### 🎥 Core Streaming Files
- **`kinect_unified_streamer.py`** - Main Kinect streaming server (runs on Pi)
- **`windows_camera_viewer_fixed.py`** - Windows camera viewer client
- **`requirements.txt`** - Python dependencies

### 🔧 Pi Setup Scripts
- **`complete_pi_setup.sh`** - Complete automated Pi setup
- **`install_freenect_from_source.sh`** - Kinect installation (GitHub gist method)
- **`setup_on_pi.sh`** - Basic Pi setup script
- **`check_libraries_on_pi.sh`** - Comprehensive Pi diagnostics

### 📤 Deployment Scripts
- **`copy_to_pi_simple.py/.bat`** - Copy setup files to Pi
- **`setup_and_start_streaming.py/.bat`** - Complete setup and start streaming

### 🔍 Diagnostic Scripts
- **`check_pi_status.py/.bat`** - Check Pi connectivity and streaming service
- **`test_fixed_viewer_diagnostic.py/.bat`** - Test camera viewer functionality

### 🚀 Launcher Scripts
- **`launch_camera_system.py/.bat`** - Comprehensive system launcher
- **`launch_working_camera_viewer.bat`** - Direct camera viewer launcher

### 📚 Documentation
- **`README.md`** - Main documentation
- **`PI_LIBRARY_DIAGNOSTIC.md`** - Pi library diagnostics guide
- **`SSH_TROUBLESHOOTING.md`** - SSH connection troubleshooting
- **`ROBUST_AUTH_SETUP.md`** - Authentication setup guide
- **`SHORTCUT_SETUP.md`** - Desktop shortcut setup
- **`MANUAL_FIX_INSTRUCTIONS.md`** - Manual fix instructions
- **`PROGRESS_SUMMARY.md`** - Development progress summary

## 🚀 Usage Workflow

### Complete Setup (Recommended)
1. **Copy files to Pi:**
   ```bash
   copy_to_pi_simple.bat
   ```

2. **Setup and start streaming:**
   ```bash
   setup_and_start_streaming.bat
   ```

3. **Launch camera viewer:**
   ```bash
   launch_working_camera_viewer.bat
   ```

### Manual Setup (Alternative)
1. **SSH to Pi:**
   ```bash
   ssh ls@192.168.1.9
   ```

2. **Run complete setup:**
   ```bash
   cd kinect_setup
   bash complete_pi_setup.sh
   ```

3. **Start streaming:**
   ```bash
   python3 kinect_unified_streamer.py
   ```

4. **View on Windows:**
   ```bash
   python windows_camera_viewer_fixed.py
   ```

## 🔧 Troubleshooting

### Check Pi Status
```bash
check_pi_status.bat
```

### Test Camera Viewer
```bash
test_fixed_viewer_diagnostic.bat
```

### Comprehensive System Launcher
```bash
launch_camera_system.bat
```

## 📋 System Requirements

### Raspberry Pi
- Raspberry Pi 3/4/5
- USB Kinect sensor
- Network connection
- Python 3.6+

### Windows
- Python 3.6+
- Network connection to Pi
- Required packages: `requests`, `pillow`, `paramiko`

## 🎯 Key Features

- **Kinect Integration**: Native freenect support with OpenCV fallback
- **HTTP Streaming**: Access camera feed via web browser
- **Real-time Display**: Low-latency streaming
- **Automated Setup**: Complete Pi setup automation
- **Comprehensive Diagnostics**: Full system health checks
- **Cross-platform**: Windows management, Linux execution

## 🔄 Development Workflow

1. **Edit code on Windows**
2. **Copy to Pi:** `copy_to_pi_simple.bat`
3. **Test on Pi:** SSH and run scripts
4. **View results:** Use camera viewer

## 📞 Support

For issues, check the troubleshooting guides in the documentation files or run the diagnostic scripts.
