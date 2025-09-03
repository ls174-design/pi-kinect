#!/usr/bin/env python3
"""
Robust file synchronization script with SSH key authentication
Eliminates password prompts and provides persistent connections
"""

import os
import sys
import argparse
import time
from pathlib import Path
from ssh_manager import SSHManager

class RobustPiSync:
    def __init__(self, pi_host, pi_user="pi", pi_path="~/kinect_ws"):
        self.pi_host = pi_host
        self.pi_user = pi_user
        self.pi_path = pi_path
        self.ssh_manager = SSHManager(pi_host, pi_user)
        
    def ensure_authentication(self):
        """Ensure SSH authentication is set up"""
        if not self.ssh_manager.test_key_authentication():
            print("🔐 Setting up SSH authentication...")
            if not self.ssh_manager.setup_complete_authentication():
                print("❌ Failed to setup SSH authentication")
                return False
        return True
    
    def run_ssh_command(self, command, timeout=30):
        """Run SSH command with robust authentication"""
        return self.ssh_manager.run_ssh_command(command, timeout)
    
    def sync_file(self, local_file, remote_file=None):
        """Sync a single file to Raspberry Pi"""
        if remote_file is None:
            remote_file = local_file
            
        local_file_path = Path(local_file)
        remote_file_path = f"{self.pi_path}/{remote_file}"
        
        if not local_file_path.exists():
            print(f"❌ Local file {local_file_path} does not exist")
            return False
            
        # Create remote directory if it doesn't exist
        remote_dir = os.path.dirname(remote_file_path)
        success, _, _ = self.run_ssh_command(f"mkdir -p {remote_dir}")
        
        # Copy file using SCP
        success, stdout, stderr = self.ssh_manager.copy_file(str(local_file_path), remote_file_path)
        
        if success:
            print(f"✅ Synced {local_file} -> {remote_file_path}")
            return True
        else:
            print(f"❌ Failed to sync {local_file}: {stderr}")
            return False
    
    def sync_directory(self, local_dir, remote_dir=None):
        """Sync entire directory to Raspberry Pi"""
        if remote_dir is None:
            remote_dir = local_dir
            
        local_path = Path(local_dir)
        if not local_path.exists():
            print(f"❌ Local directory {local_path} does not exist")
            return False
        
        print(f"📁 Syncing directory: {local_dir} -> {remote_dir}")
        
        # Create remote directory
        success, _, _ = self.run_ssh_command(f"mkdir -p {self.pi_path}/{remote_dir}")
        
        # Sync all files
        synced_count = 0
        for file_path in local_path.rglob("*"):
            if file_path.is_file():
                relative_path = file_path.relative_to(local_path)
                remote_file_path = f"{remote_dir}/{relative_path}"
                
                if self.sync_file(str(file_path), remote_file_path):
                    synced_count += 1
        
        print(f"✅ Synced {synced_count} files from {local_dir}")
        return synced_count > 0
    
    def install_dependencies(self):
        """Install dependencies on Raspberry Pi"""
        print("📦 Installing dependencies on Raspberry Pi...")
        
        # Update package list
        success, _, _ = self.run_ssh_command("sudo apt-get update", timeout=60)
        if not success:
            print("❌ Failed to update package list")
            return False
        
        # Install system packages
        packages = [
            "python3-pip",
            "python3-opencv",
            "python3-numpy",
            "python3-pil",
            "python3-dev",
            "libopencv-dev",
            "python3-opencv"
        ]
        
        for package in packages:
            print(f"📦 Installing {package}...")
            success, _, _ = self.run_ssh_command(f"sudo apt-get install -y {package}", timeout=120)
            if not success:
                print(f"⚠️ Failed to install {package}")
        
        # Install Python packages
        python_packages = [
            "opencv-python",
            "numpy",
            "pillow",
            "requests",
            "freenect"  # For Kinect support
        ]
        
        for package in python_packages:
            print(f"🐍 Installing Python package: {package}")
            success, _, _ = self.run_ssh_command(f"pip3 install {package}", timeout=60)
            if not success:
                print(f"⚠️ Failed to install Python package {package}")
        
        print("✅ Dependency installation completed")
        return True
    
    def setup_camera_streaming(self):
        """Set up camera streaming service on Raspberry Pi"""
        print("🔧 Setting up camera streaming service...")
        
        # Make scripts executable
        scripts = ["camera_streamer.py", "kinect_streamer.py"]
        for script in scripts:
            success, _, _ = self.run_ssh_command(f"chmod +x {self.pi_path}/{script}")
            if success:
                print(f"✅ Made {script} executable")
        
        # Create systemd service
        service_content = f"""[Unit]
Description=Camera Streaming Service
After=network.target

[Service]
Type=simple
User={self.pi_user}
WorkingDirectory={self.pi_path}
ExecStart=/usr/bin/python3 {self.pi_path}/camera_streamer.py
Restart=always
RestartSec=10
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
"""
        
        # Write service file
        success, _, _ = self.run_ssh_command(f"echo '{service_content}' | sudo tee /etc/systemd/system/camera-stream.service")
        if success:
            print("✅ Created systemd service file")
            
            # Reload systemd and enable service
            self.run_ssh_command("sudo systemctl daemon-reload")
            self.run_ssh_command("sudo systemctl enable camera-stream.service")
            print("✅ Enabled camera streaming service")
        else:
            print("❌ Failed to create systemd service")
            return False
        
        return True
    
    def start_camera_streaming(self):
        """Start camera streaming service"""
        print("🚀 Starting camera streaming service...")
        
        success, _, _ = self.run_ssh_command("sudo systemctl start camera-stream.service")
        if success:
            print("✅ Camera streaming service started")
            
            # Check service status
            time.sleep(2)
            success, stdout, _ = self.run_ssh_command("sudo systemctl is-active camera-stream.service")
            if success and "active" in stdout:
                print("✅ Service is running")
            else:
                print("⚠️ Service may not be running properly")
        else:
            print("❌ Failed to start camera streaming service")
            return False
        
        return True
    
    def stop_camera_streaming(self):
        """Stop camera streaming service"""
        print("⏹️ Stopping camera streaming service...")
        
        success, _, _ = self.run_ssh_command("sudo systemctl stop camera-stream.service")
        if success:
            print("✅ Camera streaming service stopped")
        else:
            print("❌ Failed to stop camera streaming service")
            return False
        
        return True
    
    def get_service_status(self):
        """Get camera streaming service status"""
        success, stdout, _ = self.run_ssh_command("sudo systemctl status camera-stream.service")
        if success:
            print("📊 Camera streaming service status:")
            print(stdout)
        else:
            print("❌ Failed to get service status")
        return success
    
    def get_pi_ip(self):
        """Get Raspberry Pi IP address"""
        success, stdout, _ = self.run_ssh_command("hostname -I | awk '{print $1}'")
        if success:
            return stdout.strip()
        return None
    
    def test_camera_stream(self):
        """Test if camera stream is accessible"""
        ip = self.get_pi_ip()
        if not ip:
            print("❌ Could not get Pi IP address")
            return False
        
        import requests
        try:
            response = requests.get(f"http://{ip}:8080/status", timeout=5)
            if response.status_code == 200:
                print(f"✅ Camera stream is accessible at http://{ip}:8080")
                return True
            else:
                print(f"❌ Camera stream returned status code: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Camera stream test failed: {e}")
            return False

def main():
    parser = argparse.ArgumentParser(description='Robust Pi Sync with SSH Key Authentication')
    parser.add_argument('--pi-host', required=True, help='Raspberry Pi hostname or IP')
    parser.add_argument('--pi-user', default='pi', help='Raspberry Pi username (default: pi)')
    parser.add_argument('--pi-path', default='~/kinect_ws', help='Remote path on Pi (default: ~/kinect_ws)')
    parser.add_argument('--setup-auth', action='store_true', help='Setup SSH authentication')
    parser.add_argument('--install-deps', action='store_true', help='Install dependencies on Pi')
    parser.add_argument('--setup-service', action='store_true', help='Set up camera streaming service')
    parser.add_argument('--start-service', action='store_true', help='Start camera streaming service')
    parser.add_argument('--stop-service', action='store_true', help='Stop camera streaming service')
    parser.add_argument('--service-status', action='store_true', help='Get service status')
    parser.add_argument('--test-stream', action='store_true', help='Test camera stream')
    parser.add_argument('--get-ip', action='store_true', help='Get Raspberry Pi IP address')
    parser.add_argument('--sync-files', action='store_true', help='Sync camera streaming files')
    
    args = parser.parse_args()
    
    sync = RobustPiSync(args.pi_host, args.pi_user, args.pi_path)
    
    # Setup authentication if requested
    if args.setup_auth:
        if not sync.ensure_authentication():
            print("❌ Authentication setup failed")
            return 1
    
    # Ensure authentication is working for other operations
    if any([args.install_deps, args.setup_service, args.start_service, 
            args.stop_service, args.service_status, args.test_stream, 
            args.get_ip, args.sync_files]):
        if not sync.ensure_authentication():
            print("❌ SSH authentication not working. Run with --setup-auth first.")
            return 1
    
    # Execute requested operations
    if args.get_ip:
        ip = sync.get_pi_ip()
        if ip:
            print(f"📍 Raspberry Pi IP: {ip}")
        else:
            print("❌ Failed to get IP address")
    
    if args.install_deps:
        sync.install_dependencies()
    
    if args.setup_service:
        sync.setup_camera_streaming()
    
    if args.start_service:
        sync.start_camera_streaming()
    
    if args.stop_service:
        sync.stop_camera_streaming()
    
    if args.service_status:
        sync.get_service_status()
    
    if args.test_stream:
        sync.test_camera_stream()
    
    if args.sync_files:
        print("📁 Syncing camera streaming files...")
        sync.sync_file("camera_streamer.py")
        sync.sync_file("kinect_streamer.py")
        sync.sync_file("requirements.txt")
    
    # Get Pi IP for easy access
    ip = sync.get_pi_ip()
    if ip:
        print(f"\n🎥 Camera stream will be available at: http://{ip}:8080")
        print(f"📱 Open this URL in your browser to view the camera feed")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
