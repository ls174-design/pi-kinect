#!/usr/bin/env python3
"""
SSH Manager for robust authentication and connection management
Handles SSH key generation, deployment, and persistent connections
"""

import os
import sys
import subprocess
import tempfile
import shutil
import stat
import time
from pathlib import Path
import json
import threading
import queue

class SSHManager:
    def __init__(self, pi_host, pi_user="pi", ssh_key_path=None):
        self.pi_host = pi_host
        self.pi_user = pi_user
        self.ssh_key_path = ssh_key_path or self._get_default_key_path()
        self.public_key_path = f"{self.ssh_key_path}.pub"
        self.connection_pool = queue.Queue(maxsize=5)
        self.connection_lock = threading.Lock()
        
    def _get_default_key_path(self):
        """Get default SSH key path"""
        home = Path.home()
        ssh_dir = home / ".ssh"
        ssh_dir.mkdir(exist_ok=True)
        # Include username in key name to avoid conflicts
        return str(ssh_dir / f"pi_kinect_{self.pi_user}_{self.pi_host.replace('.', '_')}_key")
    
    def generate_ssh_key(self, force=False):
        """Generate SSH key pair if it doesn't exist"""
        if os.path.exists(self.ssh_key_path) and not force:
            print(f"✓ SSH key already exists: {self.ssh_key_path}")
            return True
            
        try:
            # Generate SSH key pair
            cmd = [
                "ssh-keygen", "-t", "rsa", "-b", "4096",
                "-f", self.ssh_key_path,
                "-N", "",  # No passphrase
                "-C", f"pi-kinect-{self.pi_host}"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✓ Generated SSH key pair: {self.ssh_key_path}")
                
                # Set proper permissions
                os.chmod(self.ssh_key_path, stat.S_IRUSR | stat.S_IWUSR)
                os.chmod(self.public_key_path, stat.S_IRUSR | stat.S_IWUSR)
                
                return True
            else:
                print(f"✗ Failed to generate SSH key: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"✗ Error generating SSH key: {e}")
            return False
    
    def get_public_key(self):
        """Get the public key content"""
        try:
            with open(self.public_key_path, 'r') as f:
                return f.read().strip()
        except FileNotFoundError:
            return None
    
    def deploy_public_key(self, password=None):
        """Deploy public key to Raspberry Pi"""
        public_key = self.get_public_key()
        if not public_key:
            print("✗ No public key found. Generate one first.")
            return False
        
        try:
            # Create SSH directory on Pi
            ssh_dir_cmd = f"ssh {self.pi_user}@{self.pi_host} 'mkdir -p ~/.ssh && chmod 700 ~/.ssh'"
            result = subprocess.run(ssh_dir_cmd, shell=True, capture_output=True, text=True)
            
            # Add public key to authorized_keys
            auth_keys_cmd = f"echo '{public_key}' | ssh {self.pi_user}@{self.pi_host} 'cat >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys'"
            result = subprocess.run(auth_keys_cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✓ Deployed public key to {self.pi_user}@{self.pi_host}")
                return True
            else:
                print(f"✗ Failed to deploy public key: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"✗ Error deploying public key: {e}")
            return False
    
    def test_key_authentication(self):
        """Test if key-based authentication works"""
        try:
            cmd = f"ssh -i {self.ssh_key_path} -o PasswordAuthentication=no -o ConnectTimeout=10 {self.pi_user}@{self.pi_host} 'echo test'"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0 and "test" in result.stdout:
                print(f"✓ Key-based authentication working for {self.pi_user}@{self.pi_host}")
                return True
            else:
                print(f"✗ Key-based authentication failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"✗ Error testing key authentication: {e}")
            return False
    
    def run_ssh_command(self, command, timeout=30, use_key=True):
        """Run SSH command with robust authentication"""
        try:
            if use_key and os.path.exists(self.ssh_key_path):
                # Use key-based authentication
                cmd = [
                    "ssh", "-i", self.ssh_key_path,
                    "-o", "PasswordAuthentication=no",
                    "-o", "ConnectTimeout=10",
                    "-o", "ServerAliveInterval=60",
                    "-o", "ServerAliveCountMax=3",
                    f"{self.pi_user}@{self.pi_host}",
                    command
                ]
            else:
                # Fall back to password authentication
                cmd = [
                    "ssh", "-o", "ConnectTimeout=10",
                    f"{self.pi_user}@{self.pi_host}",
                    command
                ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
            return result.returncode == 0, result.stdout, result.stderr
            
        except subprocess.TimeoutExpired:
            return False, "", "Command timed out"
        except Exception as e:
            return False, "", str(e)
    
    def run_ssh_command_interactive(self, command):
        """Run SSH command with interactive output"""
        try:
            if os.path.exists(self.ssh_key_path):
                cmd = [
                    "ssh", "-i", self.ssh_key_path,
                    "-o", "PasswordAuthentication=no",
                    "-o", "ConnectTimeout=10",
                    f"{self.pi_user}@{self.pi_host}",
                    command
                ]
            else:
                cmd = [
                    "ssh", "-o", "ConnectTimeout=10",
                    f"{self.pi_user}@{self.pi_host}",
                    command
                ]
            
            # Run with real-time output
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, 
                                     universal_newlines=True, bufsize=1)
            
            return process
            
        except Exception as e:
            print(f"✗ Error running interactive SSH command: {e}")
            return None
    
    def copy_file(self, local_path, remote_path):
        """Copy file to Pi using SCP with key authentication"""
        try:
            if os.path.exists(self.ssh_key_path):
                cmd = [
                    "scp", "-i", self.ssh_key_path,
                    "-o", "PasswordAuthentication=no",
                    "-o", "ConnectTimeout=10",
                    local_path,
                    f"{self.pi_user}@{self.pi_host}:{remote_path}"
                ]
            else:
                cmd = [
                    "scp", "-o", "ConnectTimeout=10",
                    local_path,
                    f"{self.pi_user}@{self.pi_host}:{remote_path}"
                ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.returncode == 0, result.stdout, result.stderr
            
        except Exception as e:
            return False, "", str(e)
    
    def setup_ssh_config(self):
        """Set up SSH config for easier connections"""
        ssh_config_path = Path.home() / ".ssh" / "config"
        
        config_entry = f"""
Host pi-kinect-{self.pi_user}
    HostName {self.pi_host}
    User {self.pi_user}
    IdentityFile {self.ssh_key_path}
    PasswordAuthentication no
    ConnectTimeout 10
    ServerAliveInterval 60
    ServerAliveCountMax 3
"""
        
        try:
            # Read existing config
            existing_config = ""
            if ssh_config_path.exists():
                with open(ssh_config_path, 'r') as f:
                    existing_config = f.read()
            
            # Check if entry already exists
            host_name = f"pi-kinect-{self.pi_user}"
            if f"Host {host_name}" not in existing_config:
                with open(ssh_config_path, 'a') as f:
                    f.write(config_entry)
                print(f"✓ Added SSH config entry for {host_name}")
            else:
                print(f"✓ SSH config entry already exists")
            
            # Set proper permissions
            os.chmod(ssh_config_path, stat.S_IRUSR | stat.S_IWUSR)
            
            return True
            
        except Exception as e:
            print(f"✗ Error setting up SSH config: {e}")
            return False
    
    def get_connection_info(self):
        """Get connection information"""
        return {
            "pi_host": self.pi_host,
            "pi_user": self.pi_user,
            "ssh_key_path": self.ssh_key_path,
            "public_key_path": self.public_key_path,
            "key_exists": os.path.exists(self.ssh_key_path),
            "public_key_exists": os.path.exists(self.public_key_path)
        }
    
    def setup_complete_authentication(self, password=None):
        """Complete setup of SSH authentication"""
        print("🔐 Setting up SSH authentication...")
        
        # Step 1: Generate SSH key
        if not self.generate_ssh_key():
            return False
        
        # Step 2: Deploy public key
        if not self.deploy_public_key(password):
            return False
        
        # Step 3: Test authentication
        if not self.test_key_authentication():
            return False
        
        # Step 4: Setup SSH config
        if not self.setup_ssh_config():
            return False
        
        print("✅ SSH authentication setup complete!")
        print(f"   You can now connect using: ssh pi-kinect-{self.pi_user}")
        return True

def main():
    """Test the SSH manager"""
    import argparse
    
    parser = argparse.ArgumentParser(description='SSH Manager for Pi Kinect')
    parser.add_argument('--pi-host', required=True, help='Raspberry Pi hostname or IP')
    parser.add_argument('--pi-user', default='pi', help='Raspberry Pi username')
    parser.add_argument('--setup', action='store_true', help='Setup complete SSH authentication')
    parser.add_argument('--test', action='store_true', help='Test SSH connection')
    parser.add_argument('--info', action='store_true', help='Show connection info')
    
    args = parser.parse_args()
    
    ssh_manager = SSHManager(args.pi_host, args.pi_user)
    
    if args.setup:
        ssh_manager.setup_complete_authentication()
    elif args.test:
        ssh_manager.test_key_authentication()
    elif args.info:
        info = ssh_manager.get_connection_info()
        print(json.dumps(info, indent=2))
    else:
        print("Use --setup, --test, or --info")

if __name__ == '__main__':
    main()
