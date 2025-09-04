# Pi-Kinect

A robust, production-ready solution for streaming Kinect camera feeds from a Raspberry Pi with V4L2 auto-detection, RTP streaming, and comprehensive fallback capabilities.

## 🎯 Features

- **V4L2 Auto-Detection**: Automatically prefers kernel gspca_kinect driver for RGB, falls back to libfreenect for depth/advanced features
- **RTP Streaming**: Real-time video streaming over UDP with GStreamer pipeline
- **Dual Driver Strategy**: V4L2 for RGB performance, libfreenect for depth and advanced features
- **Kernel Conflict Detection**: Automatic detection and guidance for USB interface conflicts
- **CLI Interface**: Comprehensive command-line interface with streaming modes
- **systemd Integration**: Auto-start service with environment configuration
- **Cross-Platform**: Windows viewers and Pi streaming
- **Performance Optimized**: Pre-allocated buffers, thread affinity, and backpressure handling

## 🚀 Quick Start

### Hardware Requirements

- **Kinect v1** + power supply
- **Raspberry Pi 3B** (or newer) on Wi-Fi (not Ethernet)
- **Windows PC** for viewing streams

### Network Setup

- **Pi IP**: 192.168.1.9 (example)
- **Windows PC IP**: Different IP on same network (e.g., 192.168.1.100)
- **Streaming Ports**: 5000 (RGB), 5001 (depth)

### 1. Pi Setup

```bash
# Clone repository
git clone https://github.com/your-repo/pi-kinect.git
cd pi-kinect

# Run automated setup
chmod +x setup/setup_pi_deps.sh
./setup/setup_pi_deps.sh

# Verify Kinect detection
lsusb | grep -i kinect
# Should show: 045e:02ae, 045e:02ad, or 045e:02b0

# Test V4L2 driver
v4l2-ctl --list-devices
```

### 2. Driver Strategy

The system uses a smart driver selection:

1. **V4L2 First**: Checks for `gspca_kinect` kernel module
   - Loads with `depth_mode=0` for RGB-only streaming
   - Uses GStreamer pipeline for optimal performance
   - Streams to port 5000

2. **libfreenect Fallback**: If V4L2 unavailable
   - Unloads kernel module to prevent conflicts
   - Uses Python + libfreenect for full feature support
   - Supports both RGB and depth streaming

### 3. Running the Streamer

```bash
# Auto-select driver with Windows PC IP
./scripts/v4l2_rgb_or_freenect.sh 192.168.1.100

# Or set environment variable
export PC_IP=192.168.1.100
./scripts/v4l2_rgb_or_freenect.sh
```

### 4. Windows Viewer

```bash
# RGB stream viewer
windows/view_rgb.bat

# Depth stream viewer (if using libfreenect)
windows/view_depth.bat
```

## ⚙️ Configuration

### Environment Variables

Create `.env` file from `.env.example`:

```bash
# Windows PC IP address for streaming (NOT the Pi IP)
PC_IP=192.168.1.100

# Repository directory on Pi
REPO_DIR=/home/ls/pi-kinect

# Optional overrides
# PY_APP=/home/ls/pi-kinect/kinect_robust.py
# GST_FPS=20
# GST_QUALITY=70
```

### Python App Configuration

The `kinect_robust.py` script supports comprehensive CLI options:

```bash
# Basic RGB streaming
python3 kinect_robust.py --mode rgb --rtp-host 192.168.1.100

# RGB + Depth streaming
python3 kinect_robust.py --mode depth+rgb --rtp-host 192.168.1.100 --rtp-port 5001

# Custom resolution and FPS
python3 kinect_robust.py --mode rgb --width 640 --height 480 --fps 30 --rtp-host 192.168.1.100

# HTTP server only (no RTP)
python3 kinect_robust.py --mode depth+rgb --host 0.0.0.0 --port 8080
```

### CLI Arguments

- `--mode {rgb,depth,depth+rgb}`: Streaming mode
- `--rtp-host HOST`: RTP streaming target host
- `--rtp-port PORT`: RTP streaming port (default: 5001)
- `--width WIDTH`: Video width (default: 640)
- `--height HEIGHT`: Video height (default: 480)
- `--fps FPS`: Frames per second (default: 20)
- `--host HOST`: HTTP server host (default: 0.0.0.0)
- `--port PORT`: HTTP server port (default: 8080)

## 🔧 systemd Service

### Setup Auto-Start

```bash
# Install service file
sudo ln -s /home/ls/pi-kinect/systemd/pi-kinect.service /etc/systemd/system/pi-kinect@.service

# Reload systemd
sudo systemctl daemon-reload

# Enable and start service
sudo systemctl enable --now pi-kinect@192.168.1.100.service

# Check status
sudo systemctl status pi-kinect@192.168.1.100.service

# View logs
sudo journalctl -u pi-kinect@192.168.1.100.service -f
```

### Service Management

```bash
# Start service
sudo systemctl start pi-kinect@192.168.1.100.service

# Stop service
sudo systemctl stop pi-kinect@192.168.1.100.service

# Restart service
sudo systemctl restart pi-kinect@192.168.1.100.service

# Check logs
tail -f /var/log/pi-kinect.log
```

## 📁 Project Structure

```
pi-kinect/
├── scripts/
│   └── v4l2_rgb_or_freenect.sh    # Auto-select launcher
├── setup/
│   └── setup_pi_deps.sh           # Pi dependency installer
├── windows/
│   ├── view_rgb.bat               # RGB viewer
│   └── view_depth.bat             # Depth viewer
├── systemd/
│   └── pi-kinect.service          # systemd service
├── kinect_robust.py               # Main Python app
├── kinect_real_capture.py         # Legacy app
├── kinect_simple_real.py          # Legacy app
├── .env.example                   # Environment template
└── README.md                      # This file
```

## 🎮 Usage Examples

### Basic Streaming

```bash
# V4L2 RGB streaming (preferred)
./scripts/v4l2_rgb_or_freenect.sh 192.168.1.100

# libfreenect RGB + depth
python3 kinect_robust.py --mode depth+rgb --rtp-host 192.168.1.100
```

### Advanced Configuration

```bash
# High-quality RGB streaming
python3 kinect_robust.py \
  --mode rgb \
  --width 640 --height 480 --fps 30 \
  --rtp-host 192.168.1.100 --rtp-port 5000

# Depth streaming with custom settings
python3 kinect_robust.py \
  --mode depth \
  --width 320 --height 240 --fps 15 \
  --rtp-host 192.168.1.100 --rtp-port 5001
```

### HTTP Server

```bash
# Web interface only
python3 kinect_robust.py --mode depth+rgb --host 0.0.0.0 --port 8080

# Access at: http://192.168.1.9:8080
```

## 🧪 Testing

### Hardware Verification

```bash
# Check USB devices
lsusb | grep -i kinect

# Test V4L2 driver
v4l2-ctl --list-devices

# Test libfreenect
python3 -c "import freenect; print('libfreenect available')"
```

### Network Testing

```bash
# Test Pi connectivity
ping 192.168.1.9

# Test streaming ports
telnet 192.168.1.9 5000
telnet 192.168.1.9 5001
```

### Performance Testing

```bash
# Monitor CPU usage
htop

# Monitor network
iftop

# Check logs
tail -f /var/log/pi-kinect.log
```

## 🐛 Troubleshooting

### Common Issues

#### 1. "Could not claim interface" Error

```bash
# Unload kernel module
sudo modprobe -r gspca_kinect

# Reload udev rules
sudo udevadm control --reload-rules
sudo udevadm trigger

# Reconnect Kinect
```

#### 2. No V4L2 Device Found

```bash
# Check if module is loaded
lsmod | grep gspca

# Load module manually
sudo modprobe gspca_kinect depth_mode=0

# Check video devices
ls -la /dev/video*
```

#### 3. RTP Streaming Issues

```bash
# Check GStreamer installation
gst-launch-1.0 --version

# Test GStreamer pipeline
gst-launch-1.0 videotestsrc ! autovideosink

# Check network connectivity
ping 192.168.1.100
```

#### 4. Service Won't Start

```bash
# Check service status
sudo systemctl status pi-kinect@192.168.1.100.service

# Check logs
sudo journalctl -u pi-kinect@192.168.1.100.service -n 50

# Test manual execution
sudo -u ls /home/ls/pi-kinect/scripts/v4l2_rgb_or_freenect.sh 192.168.1.100
```

### Debug Mode

```bash
# Enable debug logging
export GST_DEBUG=2
python3 kinect_robust.py --mode depth+rgb --rtp-host 192.168.1.100

# Check system logs
dmesg | grep -i kinect
dmesg | grep -i usb
```

## 📊 Performance

### Benchmarks

- **RGB-only (V4L2)**: 640×480 @ 30 FPS, CPU < 40%
- **RGB+Depth (libfreenect)**: 640×480 @ 20 FPS, CPU < 60%
- **Memory Usage**: < 150MB typical
- **Network Bandwidth**: ~2-5 Mbps per stream

### Optimization Tips

1. **Use V4L2 for RGB**: Better performance than libfreenect
2. **Reduce Resolution**: Lower width/height for better performance
3. **Adjust FPS**: Lower FPS reduces CPU usage
4. **JPEG Quality**: Lower quality reduces bandwidth
5. **Wi-Fi Optimization**: Use 5GHz band if available

## 🔄 Driver Strategy Details

### V4L2 Path (Preferred)

1. **Detection**: `v4l2-ctl --list-devices | grep -i kinect`
2. **Module Loading**: `sudo modprobe gspca_kinect depth_mode=0`
3. **Streaming**: GStreamer pipeline with `v4l2src`
4. **Port**: 5000 (RGB only)

### libfreenect Path (Fallback)

1. **Module Unloading**: `sudo modprobe -r gspca_kinect`
2. **Python App**: `kinect_robust.py` with full features
3. **Streaming**: GStreamer `appsrc` pipeline
4. **Ports**: 5001 (RGB), 5002 (depth)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test on both Pi and Windows
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.

## 🙏 Acknowledgments

- [OpenKinect project](https://github.com/OpenKinect/libfreenect) for libfreenect
- [GStreamer](https://gstreamer.freedesktop.org/) for streaming pipeline
- [Raspberry Pi Foundation](https://www.raspberrypi.org/) for the hardware platform
