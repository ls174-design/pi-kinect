#!/usr/bin/env python3
"""
SSH Troubleshooting Tool for Raspberry Pi
Diagnoses and fixes common SSH authentication issues
"""

import paramiko
import os
import sys
import time
import socket
import subprocess

class SSHTroubleshooter:
    def __init__(self, pi_host, pi_user="pi", pi_password=None, pi_key_path=None):
        self.pi_host = pi_host
        self.pi_user = pi_user
        self.pi_password = pi_password
        self.pi_key_path = pi_key_path
        
    def test_network_connectivity(self):
        """Test basic network connectivity to Pi"""
        print("🌐 Testing network connectivity...")
        
        try:
            # Test ping
            result = subprocess.run(['ping', '-n', '1', self.pi_host], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                print(f"✅ Ping to {self.pi_host} successful")
            else:
                print(f"❌ Ping to {self.pi_host} failed")
                return False
        except Exception as e:
            print(f"❌ Ping test failed: {e}")
            return False
        
        # Test SSH port
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((self.pi_host, 22))
            sock.close()
            
            if result == 0:
                print(f"✅ SSH port 22 is open on {self.pi_host}")
                return True
            else:
                print(f"❌ SSH port 22 is closed on {self.pi_host}")
                return False
        except Exception as e:
            print(f"❌ SSH port test failed: {e}")
            return False
    
    def test_ssh_with_different_methods(self):
        """Test SSH connection with different authentication methods"""
        print("\n🔑 Testing SSH authentication methods...")
        
        # Method 1: Password authentication
        if self.pi_password:
            print("Testing password authentication...")
            if self._test_password_auth():
                return True
        
        # Method 2: SSH key authentication
        if self.pi_key_path and os.path.exists(self.pi_key_path):
            print("Testing SSH key authentication...")
            if self._test_key_auth():
                return True
        
        # Method 3: Try common SSH key locations
        print("Testing common SSH key locations...")
        common_key_paths = [
            os.path.expanduser("~/.ssh/id_rsa"),
            os.path.expanduser("~/.ssh/id_ed25519"),
            os.path.expanduser("~/.ssh/id_ecdsa"),
        ]
        
        for key_path in common_key_paths:
            if os.path.exists(key_path):
                print(f"Found SSH key: {key_path}")
                if self._test_key_auth(key_path):
                    return True
        
        return False
    
    def _test_password_auth(self):
        """Test password authentication"""
        try:
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            # Try with different timeout values
            for timeout in [5, 10, 15]:
                try:
                    print(f"  Trying password auth with {timeout}s timeout...")
                    ssh_client.connect(
                        hostname=self.pi_host,
                        username=self.pi_user,
                        password=self.pi_password,
                        timeout=timeout,
                        allow_agent=False,
                        look_for_keys=False
                    )
                    
                    # Test a simple command
                    stdin, stdout, stderr = ssh_client.exec_command("echo 'SSH connection successful'")
                    output = stdout.read().decode('utf-8').strip()
                    
                    if "SSH connection successful" in output:
                        print("✅ Password authentication successful!")
                        ssh_client.close()
                        return True
                    
                except paramiko.AuthenticationException:
                    print(f"  ❌ Authentication failed with {timeout}s timeout")
                except paramiko.SSHException as e:
                    print(f"  ⚠️ SSH error with {timeout}s timeout: {e}")
                except Exception as e:
                    print(f"  ⚠️ Connection error with {timeout}s timeout: {e}")
            
            ssh_client.close()
            return False
            
        except Exception as e:
            print(f"❌ Password authentication test failed: {e}")
            return False
    
    def _test_key_auth(self, key_path=None):
        """Test SSH key authentication"""
        try:
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            key_file = key_path or self.pi_key_path
            
            for timeout in [5, 10, 15]:
                try:
                    print(f"  Trying key auth with {timeout}s timeout...")
                    ssh_client.connect(
                        hostname=self.pi_host,
                        username=self.pi_user,
                        key_filename=key_file,
                        timeout=timeout,
                        allow_agent=False,
                        look_for_keys=False
                    )
                    
                    # Test a simple command
                    stdin, stdout, stderr = ssh_client.exec_command("echo 'SSH key connection successful'")
                    output = stdout.read().decode('utf-8').strip()
                    
                    if "SSH key connection successful" in output:
                        print(f"✅ SSH key authentication successful with {key_file}!")
                        ssh_client.close()
                        return True
                    
                except paramiko.AuthenticationException:
                    print(f"  ❌ Key authentication failed with {timeout}s timeout")
                except paramiko.SSHException as e:
                    print(f"  ⚠️ SSH error with {timeout}s timeout: {e}")
                except Exception as e:
                    print(f"  ⚠️ Connection error with {timeout}s timeout: {e}")
            
            ssh_client.close()
            return False
            
        except Exception as e:
            print(f"❌ SSH key authentication test failed: {e}")
            return False
    
    def check_ssh_config(self):
        """Check SSH configuration on Pi"""
        print("\n🔧 Checking SSH configuration...")
        
        # Try to connect and check SSH config
        try:
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            # Try password first
            if self.pi_password:
                ssh_client.connect(
                    hostname=self.pi_host,
                    username=self.pi_user,
                    password=self.pi_password,
                    timeout=10,
                    allow_agent=False,
                    look_for_keys=False
                )
            else:
                # Try with SSH key
                ssh_client.connect(
                    hostname=self.pi_host,
                    username=self.pi_user,
                    key_filename=self.pi_key_path,
                    timeout=10,
                    allow_agent=False,
                    look_for_keys=False
                )
            
            # Check SSH service status
            stdin, stdout, stderr = ssh_client.exec_command("systemctl is-active ssh")
            ssh_status = stdout.read().decode('utf-8').strip()
            print(f"SSH service status: {ssh_status}")
            
            # Check SSH config
            stdin, stdout, stderr = ssh_client.exec_command("sudo grep -E '^PasswordAuthentication|^PubkeyAuthentication|^PermitRootLogin' /etc/ssh/sshd_config")
            ssh_config = stdout.read().decode('utf-8').strip()
            if ssh_config:
                print("SSH configuration:")
                for line in ssh_config.split('\n'):
                    if line.strip():
                        print(f"  {line}")
            
            ssh_client.close()
            return True
            
        except Exception as e:
            print(f"❌ Could not check SSH config: {e}")
            return False
    
    def suggest_fixes(self):
        """Suggest fixes for common SSH issues"""
        print("\n💡 Suggested fixes:")
        print("1. Verify Pi IP address:")
        print(f"   - Current IP: {self.pi_host}")
        print("   - Check Pi display or run: hostname -I")
        print()
        print("2. Verify username:")
        print(f"   - Current username: {self.pi_user}")
        print("   - Default is usually 'pi'")
        print()
        print("3. Verify password:")
        print("   - Make sure Caps Lock is off")
        print("   - Try typing password in a text editor first")
        print("   - Default password is often 'raspberry'")
        print()
        print("4. Enable SSH on Pi:")
        print("   - Run: sudo systemctl enable ssh")
        print("   - Run: sudo systemctl start ssh")
        print()
        print("5. Check SSH service:")
        print("   - Run: sudo systemctl status ssh")
        print("   - Run: sudo systemctl restart ssh")
        print()
        print("6. Enable password authentication:")
        print("   - Edit: sudo nano /etc/ssh/sshd_config")
        print("   - Set: PasswordAuthentication yes")
        print("   - Restart: sudo systemctl restart ssh")
        print()
        print("7. Try different connection method:")
        print("   - Use PuTTY or Windows Terminal")
        print("   - Try: ssh pi@192.168.1.9")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='SSH Troubleshooting Tool for Raspberry Pi')
    parser.add_argument('--pi-host', required=True, help='Raspberry Pi IP address')
    parser.add_argument('--pi-user', default='pi', help='Pi username (default: pi)')
    parser.add_argument('--pi-password', help='Pi password')
    parser.add_argument('--pi-key', help='Path to SSH private key')
    
    args = parser.parse_args()
    
    print("🔍 SSH Troubleshooting Tool")
    print("=" * 50)
    print(f"Target: {args.pi_user}@{args.pi_host}")
    print("=" * 50)
    
    troubleshooter = SSHTroubleshooter(
        pi_host=args.pi_host,
        pi_user=args.pi_user,
        pi_password=args.pi_password,
        pi_key_path=args.pi_key
    )
    
    # Test network connectivity
    if not troubleshooter.test_network_connectivity():
        print("\n❌ Network connectivity issues detected!")
        troubleshooter.suggest_fixes()
        sys.exit(1)
    
    # Test SSH authentication
    if not troubleshooter.test_ssh_with_different_methods():
        print("\n❌ SSH authentication failed!")
        troubleshooter.suggest_fixes()
        sys.exit(1)
    
    # Check SSH config
    troubleshooter.check_ssh_config()
    
    print("\n✅ SSH connection is working!")
    print("You can now run the Pi setup scripts.")

if __name__ == '__main__':
    main()
