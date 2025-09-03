#!/usr/bin/env python3
"""
Fixed SSH Manager for robust authentication and connection management
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
        """Deploy public key to Raspberry Pi with improved error handling"""
        public_key = self.get_public_key()
        if not public_key:
            print("✗ No public key found. Generate one first.")
            return False
        
        try:
            # Method 1: Try using ssh-copy-id (most reliable)
            if self._try_ssh_copy_id():
                return True
            
            # Method 2: Try manual deployment with proper escaping
            if self._try_manual_deployment(public_key):
                return True
            
            # Method 3: Try using temp file method
            if self._try_temp_file_deployment(public_key):
                return True
            
            print("✗ All deployment methods failed")
            return False
                
        except Exception as e:
            print(f"✗ Error deploying public key: {e}")
            return False
    
    def _try_ssh_copy_id(self):
        """Try using ssh-copy-id command"""
        try:
            cmd = ["ssh-copy-id", "-i", self.public_key_path, f"{self.pi_user}@{self.pi_host}"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print(f"✓ Deployed public key using ssh-copy-id")
                return True
            else:
                print(f"⚠️ ssh-copy-id failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("⚠️ ssh-copy-id timed out")
            return False
        except Exception as e:
            print(f"⚠️ ssh-copy-id error: {e}")
            return False
    
    def _try_manual_deployment(self, public_key):
        """Try manual deployment with proper command construction"""
        try:
            # Create SSH directory on Pi
            ssh_dir_cmd = [
                "ssh", f"{self.pi_user}@{self.pi_host}",
                "mkdir -p ~/.ssh && chmod 700 ~/.ssh"
            ]
            result = subprocess.run(ssh_dir_cmd, capture_output=True, text=True, timeout=15)
            
            if result.returncode != 0:
                print(f"⚠️ Failed to create SSH directory: {result.stderr}")
                return False
            
            # Add public key to authorized_keys using a more robust method
            # Use printf to avoid shell interpretation issues
            auth_keys_cmd = [
                "ssh", f"{self.pi_user}@{self.pi_host}",
                f"printf '%s\\n' '{public_key}' >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys"
            ]
            result = subprocess.run(auth_keys_cmd, capture_output=True, text=True, timeout=15)
            
            if result.returncode == 0:
                print(f"✓ Deployed public key manually")
                return True
            else:
                print(f"⚠️ Manual deployment failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("⚠️ Manual deployment timed out")
            return False
        except Exception as e:
            print(f"⚠️ Manual deployment error: {e}")
            return False
    
    def _try_temp_file_deployment(self, public_key):
        """Try deployment using temporary file method"""
        try:
            # Create temporary file with public key
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.pub') as temp_file:
                temp_file.write(public_key)
                temp_file_path = temp_file.name
            
            try:
                # Copy temp file to Pi
                scp_cmd = [
                    "scp", temp_file_path,
                    f"{self.pi_user}@{self.pi_host}:~/.ssh/authorized_keys"
                ]
                result = subprocess.run(scp_cmd, capture_output=True, text=True, timeout=15)
                
                if result.returncode == 0:
                    # Set proper permissions
                    chmod_cmd = [
                        "ssh", f"{self.pi_user}@{self.pi_host}",
                        "chmod 600 ~/.ssh/authorized_keys"
                    ]
                    subprocess.run(chmod_cmd, capture_output=True, text=True, timeout=10)
                    print(f"✓ Deployed public key using temp file method")
                    return True
                else:
                    print(f"⚠️ Temp file deployment failed: {result.stderr}")
                    return False
                    
            finally:
                # Clean up temp file
                try:
                    os.unlink(temp_file_path)
                except:
                    pass
                    
        except Exception as e:
            print(f"⚠️ Temp file deployment error: {e}")
            return False
    
    def test_key_authentication(self):
        """Test if key-based authentication works"""
        try:
            cmd = [
                "ssh", "-i", self.ssh_key_path,
                "-o", "PasswordAuthentication=no",
                "-o", "ConnectTimeout=10",
                f"{self.pi_user}@{self.pi_host}",
                "echo test"
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            
            if result.returncode == 0 and "test" in result.stdout:
                print(f"✓ Key-based authentication working for {self.pi_user}@{self.pi_host}")
                return True
            else:
                print(f"✗ Key-based authentication failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("✗ Key authentication test timed out")
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
    
    def setup_complete_authentication(self, password=None):
        """Complete setup of SSH authentication with better error handling"""
        print("🔐 Setting up SSH authentication...")
        print(f"   Pi Host: {self.pi_host}")
        print(f"   Pi User: {self.pi_user}")
        print(f"   Key Path: {self.ssh_key_path}")
        
        # Step 1: Generate SSH key
        print("   Step 1: Generating SSH key...")
        if not self.generate_ssh_key():
            print("❌ Failed to generate SSH key")
            return False
        
        # Step 2: Deploy public key
        print("   Step 2: Deploying public key...")
        if not self.deploy_public_key(password):
            print("❌ Failed to deploy public key")
            print("   Try running this manually:")
            print(f"   ssh-copy-id -i {self.public_key_path} {self.pi_user}@{self.pi_host}")
            return False
        
        # Step 3: Test authentication
        print("   Step 3: Testing authentication...")
        if not self.test_key_authentication():
            print("❌ Key authentication test failed")
            return False
        
        print("✅ SSH authentication setup complete!")
        print(f"   You can now connect using: ssh -i {self.ssh_key_path} {self.pi_user}@{self.pi_host}")
        return True

def main():
    """Test the SSH manager"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Fixed SSH Manager for Pi Kinect')
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
        info = {
            "pi_host": ssh_manager.pi_host,
            "pi_user": ssh_manager.pi_user,
            "ssh_key_path": ssh_manager.ssh_key_path,
            "public_key_path": ssh_manager.public_key_path,
            "key_exists": os.path.exists(ssh_manager.ssh_key_path),
            "public_key_exists": os.path.exists(ssh_manager.public_key_path)
        }
        print(json.dumps(info, indent=2))
    else:
        print("Use --setup, --test, or --info")

if __name__ == '__main__':
    main()
