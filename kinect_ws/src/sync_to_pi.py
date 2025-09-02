#!/usr/bin/env python3
"""
File synchronization script to sync files from Windows to Raspberry Pi
"""

import os
import sys
import subprocess
import argparse
import time
from pathlib import Path

class PiSync:
    def __init__(self, pi_host, pi_user, pi_path, local_path):
        self.pi_host = pi_host
        self.pi_user = pi_user
        self.pi_path = pi_path
        self.local_path = Path(local_path)
        
    def run_ssh_command(self, command):
        """Run SSH command on Raspberry Pi"""
        ssh_cmd = f"ssh {self.pi_user}@{self.pi_host} '{command}'"
        try:
            result = subprocess.run(ssh_cmd, shell=True, capture_output=True, text=True)
            return result.returncode == 0, result.stdout, result.stderr
        except Exception as e:
            return False, "", str(e)
    
    def sync_file(self, local_file, remote_file=None):
        """Sync a single file to Raspberry Pi"""
        if remote_file is None:
            remote_file = local_file
            
        local_file_path = self.local_path / local_file
        remote_file_path = f"{self.pi_path}/{remote_file}"
        
        if not local_file_path.exists():
            print(f"Error: Local file {local_file_path} does not exist")
            return False
            
        # Create remote directory if it doesn't exist
        remote_dir = os.path.dirname(remote_file_path)
        success, _, _ = self.run_ssh_command(f"mkdir -p {remote_dir}")
        
        # Use scp to copy file
        scp_cmd = f"scp {local_file_path} {self.pi_user}@{self.pi_host}:{remote_file_path}"
        try:
            result = subprocess.run(scp_cmd, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✓ Synced {local_file} -> {remote_file_path}")
                return True
            else:
                print(f"✗ Failed to sync {local_file}: {result.stderr}")
                return False
        except Exception as e:
            print(f"✗ Error syncing {local_file}: {e}")
            return False
    
    def sync_directory(self, local_dir, remote_dir=None):
        """Sync entire directory to Raspberry Pi"""
        if remote_dir is None:
            remote_dir = local_dir
            
        local_dir_path = self.local_path / local_dir
        remote_dir_path = f"{self.pi_path}/{remote_dir}"
        
        if not local_dir_path.exists():
            print(f"Error: Local directory {local_dir_path} does not exist")
            return False
            
        # Use rsync for directory sync
        rsync_cmd = f"rsync -avz --delete {local_dir_path}/ {self.pi_user}@{self.pi_host}:{remote_dir_path}/"
        try:
            result = subprocess.run(rsync_cmd, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✓ Synced directory {local_dir} -> {remote_dir_path}")
                return True
            else:
                print(f"✗ Failed to sync directory {local_dir}: {result.stderr}")
                return False
        except Exception as e:
            print(f"✗ Error syncing directory {local_dir}: {e}")
            return False
    
    def install_dependencies(self):
        """Install required dependencies on Raspberry Pi"""
        print("Installing dependencies on Raspberry Pi...")
        
        # Update package list
        success, _, _ = self.run_ssh_command("sudo apt-get update")
        if not success:
            print("Warning: Failed to update package list")
        
        # Install Python packages
        packages = [
            "python3-pip",
            "python3-opencv",
            "python3-numpy",
            "python3-pil"
        ]
        
        for package in packages:
            success, _, _ = self.run_ssh_command(f"sudo apt-get install -y {package}")
            if success:
                print(f"✓ Installed {package}")
            else:
                print(f"✗ Failed to install {package}")
        
        # Install Python pip packages
        pip_packages = [
            "opencv-python",
            "numpy",
            "pillow"
        ]
        
        for package in pip_packages:
            success, _, _ = self.run_ssh_command(f"pip3 install {package}")
            if success:
                print(f"✓ Installed Python package {package}")
            else:
                print(f"✗ Failed to install Python package {package}")
    
    def setup_camera_streaming(self):
        """Set up camera streaming on Raspberry Pi"""
        print("Setting up camera streaming...")
        
        # Make scripts executable
        scripts = ["camera_streamer.py", "kinect_streamer.py"]
        for script in scripts:
            success, _, _ = self.run_ssh_command(f"chmod +x {self.pi_path}/{script}")
            if success:
                print(f"✓ Made {script} executable")
            else:
                print(f"✗ Failed to make {script} executable")
        
        # Create systemd service for camera streaming
        service_content = f"""[Unit]
Description=Camera Streaming Service
After=network.target

[Service]
Type=simple
User={self.pi_user}
WorkingDirectory={self.pi_path}
ExecStart=/usr/bin/python3 {self.pi_path}/camera_streamer.py --host 0.0.0.0 --port 8080
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""
        
        # Write service file
        success, _, _ = self.run_ssh_command(f"echo '{service_content}' | sudo tee /etc/systemd/system/camera-stream.service")
        if success:
            print("✓ Created systemd service")
            
            # Reload systemd and enable service
            self.run_ssh_command("sudo systemctl daemon-reload")
            self.run_ssh_command("sudo systemctl enable camera-stream.service")
            print("✓ Enabled camera streaming service")
        else:
            print("✗ Failed to create systemd service")
    
    def start_camera_streaming(self):
        """Start camera streaming service"""
        print("Starting camera streaming...")
        success, _, _ = self.run_ssh_command("sudo systemctl start camera-stream.service")
        if success:
            print("✓ Camera streaming service started")
        else:
            print("✗ Failed to start camera streaming service")
    
    def get_pi_ip(self):
        """Get Raspberry Pi IP address"""
        success, stdout, _ = self.run_ssh_command("hostname -I | awk '{print $1}'")
        if success:
            return stdout.strip()
        return None

def main():
    parser = argparse.ArgumentParser(description='Sync files to Raspberry Pi')
    parser.add_argument('--pi-host', required=True, help='Raspberry Pi hostname or IP')
    parser.add_argument('--pi-user', default='pi', help='Raspberry Pi username (default: pi)')
    parser.add_argument('--pi-path', default='~/kinect_ws', help='Remote path on Pi (default: ~/kinect_ws)')
    parser.add_argument('--local-path', default='.', help='Local path to sync (default: current directory)')
    parser.add_argument('--install-deps', action='store_true', help='Install dependencies on Pi')
    parser.add_argument('--setup-service', action='store_true', help='Set up camera streaming service')
    parser.add_argument('--start-service', action='store_true', help='Start camera streaming service')
    parser.add_argument('--get-ip', action='store_true', help='Get Raspberry Pi IP address')
    
    args = parser.parse_args()
    
    sync = PiSync(args.pi_host, args.pi_user, args.pi_path, args.local_path)
    
    if args.get_ip:
        ip = sync.get_pi_ip()
        if ip:
            print(f"Raspberry Pi IP: {ip}")
        else:
            print("Failed to get IP address")
        return
    
    if args.install_deps:
        sync.install_dependencies()
    
    if args.setup_service:
        sync.setup_camera_streaming()
    
    if args.start_service:
        sync.start_camera_streaming()
    
    # Sync camera streaming scripts
    print("Syncing camera streaming scripts...")
    sync.sync_file("camera_streamer.py")
    sync.sync_file("kinect_streamer.py")
    
    # Get Pi IP for easy access
    ip = sync.get_pi_ip()
    if ip:
        print(f"\n🎥 Camera stream will be available at: http://{ip}:8080")
        print(f"📱 Open this URL in your browser to view the camera feed")

if __name__ == '__main__':
    main()
