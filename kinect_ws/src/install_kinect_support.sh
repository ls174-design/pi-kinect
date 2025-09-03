#!/bin/bash
echo "Installing Kinect support on Raspberry Pi..."

# Update package list
echo "Updating package list..."
sudo apt-get update

# Install freenect library
echo "Installing freenect library..."
sudo apt-get install -y python3-freenect

# Install additional dependencies
echo "Installing additional dependencies..."
sudo apt-get install -y libfreenect-dev

# Install Python packages
echo "Installing Python packages..."
pip3 install freenect

echo "Kinect support installation complete!"
echo "You can now run: python3 kinect_streamer.py"
