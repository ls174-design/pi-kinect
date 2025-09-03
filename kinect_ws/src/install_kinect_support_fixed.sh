#!/bin/bash
echo "Installing Kinect support on Raspberry Pi..."

# Update package list
echo "Updating package list..."
sudo apt-get update

# Install system libraries first
echo "Installing system libraries..."
sudo apt-get install -y libfreenect-dev libfreenect0.5

# Install Python bindings
echo "Installing Python bindings..."
sudo apt-get install -y python3-freenect

# Verify installation
echo "Verifying installation..."
python3 -c "import freenect; print('✅ freenect library installed successfully')"

echo "Kinect support installation complete!"
echo "You can now run: python3 kinect_streamer.py"
