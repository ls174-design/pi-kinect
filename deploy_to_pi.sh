#!/bin/bash
set -euo pipefail

echo "🚀 Deploying Pi-Kinect to Raspberry Pi"
echo "======================================"

PI_IP="192.168.1.9"
PI_USER="pi"

# Check if Pi is reachable
echo "📡 Checking Pi connectivity..."
if ! ping -c 1 $PI_IP > /dev/null 2>&1; then
    echo "❌ Cannot reach Pi at $PI_IP"
    echo "Please check:"
    echo "1. Pi is powered on and connected to network"
    echo "2. IP address is correct"
    echo "3. SSH is enabled on Pi"
    exit 1
fi

echo "✅ Pi is reachable"

# Copy code to Pi
echo "📦 Copying pi_kinect code to Pi..."
scp -r pi_kinect $PI_USER@$PI_IP:~/

# Run setup on Pi
echo "🔧 Setting up Pi-Kinect on Pi..."
ssh $PI_USER@$PI_IP << 'EOF'
set -euo pipefail

echo "📦 Installing system dependencies..."
sudo apt-get update
sudo apt-get install -y \
    python3-pip \
    python3-dev \
    python3-opencv \
    python3-numpy \
    python3-pil \
    python3-tk \
    cmake \
    libusb-1.0-0-dev \
    libxmu-dev \
    libxi-dev \
    libgl1-mesa-dev \
    libglu1-mesa-dev \
    libxrandr-dev \
    libxinerama-dev \
    libxcursor-dev \
    swig \
    build-essential \
    libfreenect-dev \
    libfreenect0.5

# Try to install python3-freenect
if sudo apt-get install -y python3-freenect 2>/dev/null; then
    echo "✅ python3-freenect installed from package"
else
    echo "⚠️ python3-freenect not available in repositories"
fi

# Install Pi-Kinect
echo "🐍 Installing Pi-Kinect..."
cd ~/pi_kinect
pip3 install -e .

# Set up udev rules
echo "🔧 Setting up udev rules..."
sudo tee /etc/udev/rules.d/51-kinect.rules > /dev/null << 'UDEV_EOF'
# Kinect v1 udev rules
SUBSYSTEM=="usb", ATTR{idVendor}=="045e", ATTR{idProduct}=="02b0", MODE="0666"
SUBSYSTEM=="usb", ATTR{idVendor}=="045e", ATTR{idProduct}=="02ad", MODE="0666"
SUBSYSTEM=="usb", ATTR{idVendor}=="045e", ATTR{idProduct}=="02ae", MODE="0666"
SUBSYSTEM=="usb", ATTR{idVendor}=="045e", ATTR{idProduct}=="02c2", MODE="0666"
SUBSYSTEM=="usb", ATTR{idVendor}=="045e", ATTR{idProduct}=="02be", MODE="0666"
SUBSYSTEM=="usb", ATTR{idVendor}=="045e", ATTR{idProduct}=="02bf", MODE="0666"
UDEV_EOF

# Reload udev rules
sudo udevadm control --reload-rules
sudo udevadm trigger

# Add user to required groups
sudo adduser pi video
sudo adduser pi plugdev

echo "✅ Setup complete!"
echo ""
echo "🎯 Next steps:"
echo "1. Reboot your Pi or log out/in to apply group changes"
echo "2. Test with: pi-kinect probe --verbose"
echo "3. Start streaming with: pi-kinect stream --host 0.0.0.0 --port 8080"
echo "4. Open http://$PI_IP:8080 in your browser"
EOF

echo ""
echo "🎉 Deployment complete!"
echo ""
echo "📋 To start the Kinect streamer:"
echo "1. SSH into your Pi: ssh $PI_USER@$PI_IP"
echo "2. Run: pi-kinect stream --host 0.0.0.0 --port 8080"
echo "3. Open http://$PI_IP:8080 in your browser"
echo ""
echo "🔍 To test Kinect detection:"
echo "ssh $PI_USER@$PI_IP 'pi-kinect probe --verbose'"
