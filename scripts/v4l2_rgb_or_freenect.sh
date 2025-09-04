#!/usr/bin/env bash
set -Eeuo pipefail

# Configuration with defaults
PC_IP="${1:-${PC_IP:-}}"
REPO_DIR="${REPO_DIR:-$HOME/pi-kinect}"
PY_APP="${PY_APP:-$REPO_DIR/kinect_robust.py}"
GST_FPS="${GST_FPS:-20}"
GST_QUALITY="${GST_QUALITY:-70}"

if [[ -z "${PC_IP}" ]]; then
  echo "❌ Usage: $0 <WINDOWS_PC_IP>"
  echo "   Example: $0 192.168.1.100"
  echo "   Or set PC_IP environment variable"
  exit 1
fi

echo "🎯 Pi-Kinect Auto-Select Launcher"
echo "📡 Target PC IP: ${PC_IP}"
echo "📁 Repo directory: ${REPO_DIR}"
echo ""

# Check for Kinect V4L2 node
echo "[INFO] Checking for Kinect V4L2 node..."
if v4l2-ctl --list-devices 2>/dev/null | grep -qi "Kinect"; then
  echo "✅ Found Kinect V4L2 device"
  
  # Load gspca_kinect module with depth_mode=0 (RGB only)
  echo "🔧 Loading gspca_kinect kernel module..."
  sudo modprobe gspca_kinect depth_mode=0 || true
  
  # Find the video device
  DEV="/dev/video0"
  if [[ -e "${DEV}" ]]; then
    echo "📹 [RGB via V4L2] Streaming ${DEV} → ${PC_IP}:5000"
    echo "   Format: RTP/MJPEG ${GST_FPS} fps, quality=${GST_QUALITY}"
    echo "   Press Ctrl+C to stop"
    echo ""
    
    # GStreamer pipeline for V4L2 RGB streaming
    exec gst-launch-1.0 v4l2src device="${DEV}" ! \
      video/x-raw,width=640,height=480,framerate=${GST_FPS}/1 ! \
      videoconvert ! jpegenc quality=${GST_QUALITY} ! rtpjpegpay ! \
      udpsink host="${PC_IP}" port=5000
  else
    echo "❌ Video device ${DEV} not found"
    exit 1
  fi
else
  echo "⚠️  No Kinect V4L2 device found, falling back to libfreenect"
fi

# Fallback to libfreenect
echo "[Fallback libfreenect] Unloading kernel module and launching Python..."
sudo modprobe -r gspca_kinect || true

if [[ ! -f "${PY_APP}" ]]; then
  echo "❌ Missing ${PY_APP}"
  echo "   Set REPO_DIR or PY_APP environment variable accordingly"
  exit 2
fi

echo "🐍 [libfreenect] Launching Python app..."
echo "   App: ${PY_APP}"
echo "   Target: ${PC_IP}:5001 (depth+rgb)"
echo "   Press Ctrl+C to stop"
echo ""

# Launch Python app with RTP streaming
exec python3 "${PY_APP}" --mode depth+rgb --rtp-host "${PC_IP}" --rtp-port 5001
