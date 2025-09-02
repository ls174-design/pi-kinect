# Raspberry Pi Camera Streaming Setup

This project provides a complete solution for streaming camera feeds from a Raspberry Pi to a Windows laptop, bypassing the Cursor Remote SSH ARM architecture limitations.

## 🎯 Quick Start

### 1. Set up Raspberry Pi

```bash
# SSH into your Raspberry Pi
ssh pi@192.168.1.9  # Replace with your Pi's IP

# Install dependencies
sudo apt-get update
sudo apt-get install -y python3-pip python3-opencv python3-numpy python3-pil

# Install Python packages
pip3 install opencv-python numpy pillow requests
```

### 2. Sync files to Raspberry Pi

From your Windows machine:

```bash
# Navigate to the project directory
cd "C:\Users\lysan\pi backup\kinect_ws\src"

# Sync files to Pi
python sync_to_pi.py --pi-host 192.168.1.9 --pi-user pi --install-deps --setup-service --start-service
```

### 3. View camera feed on Windows

```bash
# Run the Windows camera viewer
python windows_camera_viewer.py
```

## 📁 Project Structure

```
kinect_ws/src/
├── camera_streamer.py      # Basic camera streaming server
├── kinect_streamer.py      # Kinect-specific streaming server
├── sync_to_pi.py          # File synchronization script
├── windows_camera_viewer.py # Windows client application
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## 🚀 Features

### Camera Streaming Server (Raspberry Pi)
- **HTTP-based streaming**: Access camera feed via web browser
- **Multiple formats**: RGB, depth (for Kinect), and IR streams
- **Real-time display**: Low-latency streaming with configurable quality
- **REST API**: JSON endpoints for frame data and status
- **Auto-restart**: Systemd service for automatic startup

### Windows Client Application
- **GUI interface**: Easy-to-use Tkinter-based viewer
- **Real-time display**: Live camera feed with 10 FPS update rate
- **Frame capture**: Save individual frames as JPEG images
- **Connection management**: Connect/disconnect with status monitoring
- **Configurable**: Set Pi IP address and port

### File Synchronization
- **Automated sync**: Push code changes to Pi automatically
- **Dependency management**: Install required packages on Pi
- **Service setup**: Configure systemd services for auto-start
- **Cross-platform**: Works on Windows, Linux, and macOS

## 🎮 Usage

### Basic Camera Streaming

1. **Start the camera server on Pi:**
   ```bash
   python3 camera_streamer.py --host 0.0.0.0 --port 8080
   ```

2. **Access via web browser:**
   ```
   http://192.168.1.9:8080
   ```

3. **Or use the Windows client:**
   ```bash
   python windows_camera_viewer.py
   ```

### Kinect Streaming

1. **Install Kinect dependencies on Pi:**
   ```bash
   sudo apt-get install python3-freenect
   # or
   pip3 install freenect
   ```

2. **Start Kinect server:**
   ```bash
   python3 kinect_streamer.py --host 0.0.0.0 --port 8080
   ```

3. **View RGB and depth streams:**
   ```
   http://192.168.1.9:8080
   ```

### Development Workflow

1. **Make changes on Windows**
2. **Sync to Pi:**
   ```bash
   python sync_to_pi.py --pi-host 192.168.1.9
   ```
3. **Test on Pi:**
   ```bash
   ssh pi@192.168.1.9
   python3 camera_streamer.py
   ```

## 🔧 Configuration

### Camera Settings

Edit `camera_streamer.py` to modify:
- **Resolution**: Default 640x480
- **Frame rate**: Default 30 FPS
- **JPEG quality**: Default 85%
- **Camera index**: Default 0 (first camera)

### Network Settings

- **Host**: Bind to all interfaces (0.0.0.0) or specific IP
- **Port**: Default 8080 (change if needed)
- **Firewall**: Ensure port is open on Pi

### Service Configuration

The systemd service runs automatically on boot:
```bash
# Check service status
sudo systemctl status camera-stream.service

# Restart service
sudo systemctl restart camera-stream.service

# View logs
sudo journalctl -u camera-stream.service -f
```

## 🐛 Troubleshooting

### Connection Issues

1. **Check Pi IP address:**
   ```bash
   hostname -I
   ```

2. **Test connectivity:**
   ```bash
   ping 192.168.1.9
   ```

3. **Check if service is running:**
   ```bash
   sudo systemctl status camera-stream.service
   ```

### Camera Issues

1. **Check camera permissions:**
   ```bash
   ls -la /dev/video*
   ```

2. **Test camera manually:**
   ```bash
   python3 -c "import cv2; cap = cv2.VideoCapture(0); print('Camera available:', cap.isOpened())"
   ```

3. **Try different camera index:**
   ```bash
   python3 camera_streamer.py --camera 1
   ```

### Performance Issues

1. **Reduce frame rate:**
   - Edit `camera_streamer.py` and change the sleep time in `capture_frames()`

2. **Lower JPEG quality:**
   - Change `cv2.IMWRITE_JPEG_QUALITY` value (lower = smaller files)

3. **Reduce resolution:**
   - Modify `cap.set(cv2.CAP_PROP_FRAME_WIDTH/HEIGHT)` values

## 🔄 Alternative Development Approaches

Since Cursor Remote SSH doesn't support ARM:

### 1. VS Code Remote SSH
- Install VS Code with Remote SSH extension
- Better ARM support than Cursor
- Full development environment on Pi

### 2. File Sync + Terminal
- Use `sync_to_pi.py` for file synchronization
- SSH for terminal access
- Edit on Windows, test on Pi

### 3. Git-based Workflow
- Push changes to Git repository
- Pull on Pi for testing
- Automated deployment with webhooks

### 4. Docker Development
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

## 🙏 Acknowledgments

- OpenKinect project for libfreenect
- OpenCV community for computer vision tools
- Raspberry Pi Foundation for the amazing hardware
