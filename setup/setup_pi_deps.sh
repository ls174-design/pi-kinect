#!/usr/bin/env bash
set -Eeuo pipefail

echo "🔧 Setting up Pi dependencies for Kinect streaming..."

# Update package lists
echo "📦 Updating package lists..."
sudo apt-get update

# Install essential packages
echo "📦 Installing essential packages..."
sudo apt-get install -y \
  git build-essential cmake pkg-config \
  libusb-1.0-0-dev libglfw3-dev libudev-dev \
  python3 python3-dev python3-numpy \
  gstreamer1.0-tools gstreamer1.0-plugins-base \
  gstreamer1.0-plugins-good gstreamer1.0-plugins-bad \
  gstreamer1.0-libav v4l-utils curl gnupg lsb-release

# ROS apt key (keyring) + single list file (optional; needed only if using ROS)
echo "🔑 Setting up ROS repository (optional)..."
sudo rm -f /etc/apt/sources.list.d/ros-latest.list
sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.asc \
| sudo gpg --dearmor -o /usr/share/keyrings/ros-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] \
http://packages.ros.org/ros/ubuntu $(lsb_release -sc) main" \
| sudo tee /etc/apt/sources.list.d/ros1-latest.list >/dev/null || true

# libfreenect (Kinect v1)
echo "🔧 Building libfreenect from source..."
cd ~
if [ ! -d libfreenect ]; then 
  echo "📥 Cloning libfreenect repository..."
  git clone https://github.com/OpenKinect/libfreenect.git
fi

cd libfreenect && mkdir -p build && cd build
echo "🔨 Configuring libfreenect build..."
cmake .. -DBUILD_PYTHON3=ON
echo "🔨 Building libfreenect (this may take a while)..."
make -j4
echo "📦 Installing libfreenect..."
sudo make install && sudo ldconfig

# udev rules for non-root Kinect access
echo "🔐 Setting up udev rules for Kinect access..."
cd ~/libfreenect
sudo cp platform/linux/udev/51-kinect.rules /etc/udev/rules.d/
sudo udevadm control --reload-rules && sudo udevadm trigger

echo "✅ Pi dependencies setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Reboot the Pi or run: sudo udevadm control --reload-rules"
echo "2. Check Kinect detection: lsusb | grep -i kinect"
echo "3. Test V4L2 driver: v4l2-ctl --list-devices"
echo "4. Run the streaming script: ./scripts/v4l2_rgb_or_freenect.sh <WINDOWS_PC_IP>"
