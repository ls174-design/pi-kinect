#!/usr/bin/env python3
"""
Run comprehensive diagnostic on Raspberry Pi
This script connects to the Pi and runs the library check
"""

import paramiko
import sys
import time
import os
from pathlib import Path

class PiDiagnostic:
    def __init__(self, pi_host, pi_user="pi", pi_password=None, pi_key_path=None):
        self.pi_host = pi_host
        self.pi_user = pi_user
        self.pi_password = pi_password
        self.pi_key_path = pi_key_path
        self.ssh_client = None
        
    def connect(self):
        """Connect to Raspberry Pi via SSH"""
        print(f"🔌 Connecting to Raspberry Pi at {self.pi_host}...")
        
        try:
            self.ssh_client = paramiko.SSHClient()
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            if self.pi_key_path and os.path.exists(self.pi_key_path):
                print(f"🔑 Using SSH key: {self.pi_key_path}")
                self.ssh_client.connect(
                    hostname=self.pi_host,
                    username=self.pi_user,
                    key_filename=self.pi_key_path,
                    timeout=10
                )
            elif self.pi_password:
                print("🔑 Using password authentication")
                self.ssh_client.connect(
                    hostname=self.pi_host,
                    username=self.pi_user,
                    password=self.pi_password,
                    timeout=10
                )
            else:
                print("❌ No authentication method provided")
                return False
            
            print("✅ Connected to Raspberry Pi successfully")
            return True
            
        except Exception as e:
            print(f"❌ Failed to connect to Raspberry Pi: {e}")
            return False
    
    def run_command(self, command, timeout=30):
        """Run a command on the Pi and return output"""
        try:
            stdin, stdout, stderr = self.ssh_client.exec_command(command, timeout=timeout)
            
            # Wait for command to complete
            exit_status = stdout.channel.recv_exit_status()
            
            output = stdout.read().decode('utf-8')
            error = stderr.read().decode('utf-8')
            
            return exit_status == 0, output, error
            
        except Exception as e:
            return False, "", str(e)
    
    def upload_file(self, local_path, remote_path):
        """Upload a file to the Pi"""
        try:
            sftp = self.ssh_client.open_sftp()
            sftp.put(local_path, remote_path)
            sftp.close()
            return True
        except Exception as e:
            print(f"❌ Failed to upload {local_path}: {e}")
            return False
    
    def download_file(self, remote_path, local_path):
        """Download a file from the Pi"""
        try:
            sftp = self.ssh_client.open_sftp()
            sftp.get(remote_path, local_path)
            sftp.close()
            return True
        except Exception as e:
            print(f"❌ Failed to download {remote_path}: {e}")
            return False
    
    def run_library_check(self):
        """Run the library check on the Pi"""
        print("\n🔍 Running library diagnostic on Raspberry Pi...")
        
        # Upload the diagnostic script
        local_script = "check_pi_libraries.py"
        remote_script = f"/home/{self.pi_user}/check_pi_libraries.py"
        
        if not os.path.exists(local_script):
            print(f"❌ Diagnostic script not found: {local_script}")
            return False
        
        print(f"📤 Uploading diagnostic script...")
        if not self.upload_file(local_script, remote_script):
            return False
        
        # Make script executable
        success, output, error = self.run_command(f"chmod +x {remote_script}")
        if not success:
            print(f"⚠️ Failed to make script executable: {error}")
        
        # Run the diagnostic
        print("🚀 Running diagnostic...")
        success, output, error = self.run_command(f"python3 {remote_script}", timeout=60)
        
        if success:
            print("✅ Diagnostic completed successfully")
            print("\n" + "="*60)
            print("DIAGNOSTIC OUTPUT:")
            print("="*60)
            print(output)
            if error:
                print("\nWARNINGS/ERRORS:")
                print(error)
        else:
            print("❌ Diagnostic failed")
            print("Error:", error)
            print("Output:", output)
        
        return success
    
    def install_libraries(self):
        """Install missing libraries on the Pi"""
        print("\n🔧 Installing libraries on Raspberry Pi...")
        
        # Upload the installation script
        local_script = "install_pi_libraries.sh"
        remote_script = f"/home/{self.pi_user}/install_pi_libraries.sh"
        
        if not os.path.exists(local_script):
            print(f"❌ Installation script not found: {local_script}")
            return False
        
        print(f"📤 Uploading installation script...")
        if not self.upload_file(local_script, remote_script):
            return False
        
        # Make script executable
        success, output, error = self.run_command(f"chmod +x {remote_script}")
        if not success:
            print(f"⚠️ Failed to make script executable: {error}")
        
        # Run the installation
        print("🚀 Running installation (this may take several minutes)...")
        success, output, error = self.run_command(f"bash {remote_script}", timeout=600)
        
        if success:
            print("✅ Installation completed successfully")
            print("\n" + "="*60)
            print("INSTALLATION OUTPUT:")
            print("="*60)
            print(output)
            if error:
                print("\nWARNINGS/ERRORS:")
                print(error)
        else:
            print("❌ Installation failed")
            print("Error:", error)
            print("Output:", output)
        
        return success
    
    def check_streaming_service(self):
        """Check if the streaming service is running"""
        print("\n🌐 Checking streaming service status...")
        
        # Check if port 8080 is in use
        success, output, error = self.run_command("netstat -tuln | grep 8080")
        if success and output.strip():
            print("✅ Streaming service appears to be running on port 8080")
            print(f"Port status: {output.strip()}")
        else:
            print("❌ No service running on port 8080")
        
        # Check for running Python processes
        success, output, error = self.run_command("ps aux | grep python | grep -v grep")
        if success and output.strip():
            print("✅ Python processes found:")
            for line in output.strip().split('\n'):
                if 'kinect' in line.lower() or 'stream' in line.lower():
                    print(f"  {line}")
        else:
            print("❌ No relevant Python processes found")
    
    def disconnect(self):
        """Disconnect from the Pi"""
        if self.ssh_client:
            self.ssh_client.close()
            print("🔌 Disconnected from Raspberry Pi")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Run diagnostic on Raspberry Pi')
    parser.add_argument('--pi-host', required=True, help='Raspberry Pi IP address')
    parser.add_argument('--pi-user', default='pi', help='Pi username (default: pi)')
    parser.add_argument('--pi-password', help='Pi password')
    parser.add_argument('--pi-key', help='Path to SSH private key')
    parser.add_argument('--install', action='store_true', help='Install missing libraries')
    parser.add_argument('--check-service', action='store_true', help='Check streaming service status')
    
    args = parser.parse_args()
    
    # Create diagnostic instance
    diagnostic = PiDiagnostic(
        pi_host=args.pi_host,
        pi_user=args.pi_user,
        pi_password=args.pi_password,
        pi_key_path=args.pi_key
    )
    
    try:
        # Connect to Pi
        if not diagnostic.connect():
            sys.exit(1)
        
        # Run library check
        diagnostic.run_library_check()
        
        # Install libraries if requested
        if args.install:
            diagnostic.install_libraries()
            # Re-run diagnostic after installation
            print("\n🔄 Re-running diagnostic after installation...")
            diagnostic.run_library_check()
        
        # Check streaming service if requested
        if args.check_service:
            diagnostic.check_streaming_service()
        
    except KeyboardInterrupt:
        print("\n⏹️ Operation cancelled by user")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    finally:
        diagnostic.disconnect()

if __name__ == '__main__':
    main()
