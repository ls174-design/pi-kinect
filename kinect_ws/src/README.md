# Raspberry Pi Kinect Streaming Setup

This project provides a complete solution for streaming Kinect camera feeds from a Raspberry Pi to a Windows laptop, with comprehensive diagnostic tools and automated setup scripts.

## 🎯 Quick Start

### 1. Automated Setup (Recommended)

From your Windows machine:

```bash
# Navigate to the project directory
cd "C:\Users\lysan\Desktop\pi-kinect\kinect_ws\src"

# Copy setup files to Pi
copy_to_pi_simple.bat

# Follow the prompts to enter your Pi's IP, username, and password
```

Then on your Raspberry Pi:

```bash
# SSH into your Pi
ssh pi@192.168.1.9  # Replace with your Pi's IP

# Run the complete setup
cd kinect_setup
bash complete_pi_setup.sh
```

### 2. Manual Setup (Alternative)

If you prefer manual installation:

```bash
# SSH into your Raspberry Pi
ssh pi@192.168.1.9  # Replace with your Pi's IP

# Install Kinect dependencies (following GitHub gist method)
bash install_freenect_from_source.sh

# Install other dependencies
sudo apt-get install -y python3-pip python3-opencv python3-numpy python3-pil
pip3 install opencv-python numpy pillow requests
```

### 3. Test the Setup

```bash
# Check if everything is working
bash check_libraries_on_pi.sh

# Start the Kinect streamer
python3 kinect_unified_streamer.py
```

### 4. View Kinect feed on Windows

```bash
# Run the Windows camera viewer
python windows_camera_viewer.py
```

## 📁 Project Structure

```
kinect_ws/src/
├── kinect_unified_streamer.py    # Main Kinect streaming server (with fallback to OpenCV)
├── windows_camera_viewer.py      # Windows client application
├── requirements.txt              # Python dependencies
├── 
├── 🔧 Setup Scripts:
├── complete_pi_setup.sh          # Complete automated setup for Pi
├── install_freenect_from_source.sh # Kinect installation (GitHub gist method)
├── setup_on_pi.sh               # Basic Pi setup script
├── check_libraries_on_pi.sh     # Comprehensive diagnostic script
├── 
├── 📤 Deployment Scripts:
├── copy_to_pi_simple.py/.bat    # Copy setup files to Pi
├── robust_pi_setup.py/.bat      # Robust Pi setup with error handling
├── manual_pi_setup.py/.bat      # Step-by-step manual setup
├── 
├── 🔍 Diagnostic Scripts:
├── check_pi_libraries.py        # Python diagnostic script
├── ssh_troubleshoot.py/.bat     # SSH connectivity diagnostics
├── kinect_diagnostic.py         # Kinect-specific diagnostics
├── 
└── README.md                    # This file
```

## 🚀 Features

### Kinect Streaming Server (Raspberry Pi)
- **Kinect Integration**: Native freenect support with OpenCV fallback
- **HTTP-based streaming**: Access camera feed via web browser
- **Multiple formats**: RGB, depth (for Kinect), and IR streams
- **Real-time display**: Low-latency streaming with configurable quality
- **REST API**: JSON endpoints for frame data and status
- **Auto-fallback**: Automatically switches to OpenCV if Kinect unavailable

### Windows Client Application
- **GUI interface**: Easy-to-use Tkinter-based viewer
- **Real-time display**: Live camera feed with 10 FPS update rate
- **Frame capture**: Save individual frames as JPEG images
- **Connection management**: Connect/disconnect with status monitoring
- **Configurable**: Set Pi IP address and port

### Automated Setup & Diagnostics
- **Complete setup scripts**: Automated installation of all dependencies
- **Comprehensive diagnostics**: Check hardware, libraries, and connectivity
- **Multiple installation methods**: System packages, pip, and source builds
- **Error handling**: Robust scripts with detailed error reporting
- **Cross-platform deployment**: Windows batch files for easy Pi management

## 🎮 Usage

### Kinect Streaming (Primary Method)

1. **Start the Kinect server on Pi:**
   ```bash
   python3 kinect_unified_streamer.py
   ```

2. **Access via web browser:**
   ```
   http://192.168.1.9:8080
   ```

3. **Or use the Windows client:**
   ```bash
   python windows_camera_viewer.py
   ```

### Diagnostic & Setup Commands

1. **Check system status:**
   ```bash
   bash check_libraries_on_pi.sh
   ```

2. **Install Kinect dependencies:**
   ```bash
   bash install_freenect_from_source.sh
   ```

3. **Complete system setup:**
   ```bash
   bash complete_pi_setup.sh
   ```

### Development Workflow

1. **Make changes on Windows**
2. **Copy files to Pi:**
   ```bash
   copy_to_pi_simple.bat
   ```
3. **Test on Pi:**
   ```bash
   ssh pi@192.168.1.9
   cd kinect_setup
   python3 kinect_unified_streamer.py
   ```

## 🔧 Configuration

### Kinect Settings

Edit `kinect_unified_streamer.py` to modify:
- **Resolution**: Default 640x480
- **Frame rate**: Default 30 FPS
- **JPEG quality**: Default 85%
- **Fallback behavior**: OpenCV camera index (default 0)

### Network Settings

- **Host**: Bind to all interfaces (0.0.0.0) or specific IP
- **Port**: Default 8080 (change if needed)
- **Firewall**: Ensure port is open on Pi

### Installation Methods

The setup scripts support multiple installation approaches:

1. **System packages** (preferred when available):
   ```bash
   sudo apt-get install libfreenect-dev libfreenect0.5
   ```

2. **Source build** (GitHub gist method):
   ```bash
   bash install_freenect_from_source.sh
   ```

3. **Complete automated setup**:
   ```bash
   bash complete_pi_setup.sh
   ```

## 🐛 Troubleshooting

### Quick Diagnostics

1. **Run comprehensive diagnostics:**
   ```bash
   bash check_libraries_on_pi.sh
   ```

2. **Check SSH connectivity:**
   ```bash
   ssh_troubleshoot.bat
   ```

3. **Test Kinect specifically:**
   ```bash
   python3 kinect_diagnostic.py
   ```

### Common Issues

#### Kinect Not Detected
1. **Check USB connection:**
   ```bash
   lsusb | grep -i microsoft
   ```

2. **Verify udev rules:**
   ```bash
   ls -la /etc/udev/rules.d/51-kinect.rules
   ```

3. **Test freenect directly:**
   ```bash
   freenect-glview
   ```

#### Python Import Errors
1. **Check freenect installation:**
   ```bash
   python3 -c "import freenect; print('Freenect available')"
   ```

2. **Reinstall if needed:**
   ```bash
   bash install_freenect_from_source.sh
   ```

#### Connection Issues
1. **Check Pi IP address:**
   ```bash
   hostname -I
   ```

2. **Test connectivity:**
   ```bash
   ping 192.168.1.9
   ```

3. **Verify streaming service:**
   ```bash
   curl http://192.168.1.9:8080/status
   ```

### Performance Issues

1. **Reduce frame rate:**
   - Edit `kinect_unified_streamer.py` and change the sleep time in `capture_frames()`

2. **Lower JPEG quality:**
   - Change `cv2.IMWRITE_JPEG_QUALITY` value (lower = smaller files)

3. **Reduce resolution:**
   - Modify `cap.set(cv2.CAP_PROP_FRAME_WIDTH/HEIGHT)` values

## 🔄 Development Workflow

### Recommended Approach: File Sync + SSH

1. **Edit code on Windows** (using Cursor or VS Code)
2. **Copy files to Pi:**
   ```bash
   copy_to_pi_simple.bat
   ```
3. **Test on Pi via SSH:**
   ```bash
   ssh pi@192.168.1.9
   cd kinect_setup
   python3 kinect_unified_streamer.py
   ```

### Alternative Development Methods

### 1. VS Code Remote SSH
- Install VS Code with Remote SSH extension
- Better ARM support than Cursor
- Full development environment on Pi

### 2. Git-based Workflow
- Push changes to Git repository
- Pull on Pi for testing
- Automated deployment with webhooks

### 3. Docker Development
- Containerize the application
- Run on both Windows and Pi
- Consistent development environment

## 📚 API Reference

### HTTP Endpoints

- `GET /` - Camera viewer web page
- `GET /stream` - Raw video stream (MJPEG)
- `GET /frame` - Single frame as JSON
- `GET /status` - Server status information

### JSON Response Format

```json
{
  "timestamp": 1640995200.123,
  "width": 640,
  "height": 480,
  "format": "jpeg",
  "data": "base64_encoded_image_data"
}
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test on both Windows and Pi
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📋 Installation Methods Reference

### Kinect Installation (GitHub Gist Method)

The project uses the proven installation method from [this GitHub gist](https://gist.github.com/Collin-Emerson-Miller/8b4630c767aeb4a0b324ea4070c3db9d):

1. **System dependencies:**
   ```bash
   sudo apt-get install git-core cmake freeglut3-dev pkg-config build-essential libxmu-dev libxi-dev libusb-1.0-0-dev cython python3-dev python3-numpy
   ```

2. **Build libfreenect:**
   ```bash
   git clone git://github.com/OpenKinect/libfreenect.git
   cd libfreenect
   mkdir build && cd build
   cmake -L ..
   make
   sudo make install
   sudo ldconfig /usr/local/lib64/
   ```

3. **Install Python bindings:**
   ```bash
   cd ../wrappers/python
   sudo python3 setup.py install
   ```

4. **Set up USB permissions:**
   ```bash
   sudo adduser $USER video
   sudo adduser $USER plugdev
   # Create udev rules (handled by setup scripts)
   ```

## 🙏 Acknowledgments

- [OpenKinect project](https://github.com/OpenKinect/libfreenect) for libfreenect
- [GitHub gist by Collin-Emerson-Miller](https://gist.github.com/Collin-Emerson-Miller/8b4630c767aeb4a0b324ea4070c3db9d) for the proven installation method
- OpenCV community for computer vision tools
- Raspberry Pi Foundation for the amazing hardware
