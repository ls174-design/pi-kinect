#!/usr/bin/env python3
"""
Complete Raspberry Pi setup: Deploy, Install, and Check
"""

import paramiko
import os
import sys
import time

class PiSetup:
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
    
    def run_command(self, command, timeout=60):
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
    
    def deploy_files(self):
        """Deploy diagnostic files to Pi"""
        print("\n📤 Deploying diagnostic files...")
        
        # Create directory
        success, output, error = self.run_command("mkdir -p kinect_diagnostic")
        
        # Files to deploy
        files_to_deploy = [
            "check_pi_libraries.py",
            "install_pi_libraries.sh"
        ]
        
        for filename in files_to_deploy:
            if os.path.exists(filename):
                print(f"📤 Uploading {filename}...")
                remote_path = f"kinect_diagnostic/{filename}"
                if self.upload_file(filename, remote_path):
                    print(f"✅ {filename} uploaded successfully")
                    
                    # Make executable if it's a shell script
                    if filename.endswith('.sh'):
                        success, output, error = self.run_command(f"chmod +x {remote_path}")
                        if success:
                            print(f"✅ Made {filename} executable")
                else:
                    print(f"❌ Failed to upload {filename}")
                    return False
            else:
                print(f"❌ {filename} not found locally")
                return False
        
        return True
    
    def install_libraries(self):
        """Install libraries on Pi"""
        print("\n🔧 Installing libraries on Raspberry Pi...")
        print("This may take 10-15 minutes...")
        
        # Run the installation script
        success, output, error = self.run_command("cd kinect_diagnostic && bash install_pi_libraries.sh", timeout=900)
        
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
    
    def run_diagnostic(self):
        """Run diagnostic check on Pi"""
        print("\n🔍 Running diagnostic check...")
        
        # Run the diagnostic script
        success, output, error = self.run_command("cd kinect_diagnostic && python3 check_pi_libraries.py", timeout=120)
        
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
    
    def check_streaming_service(self):
        """Check if streaming service is running"""
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
    
    parser = argparse.ArgumentParser(description='Complete Pi setup: Deploy, Install, and Check')
    parser.add_argument('--pi-host', required=True, help='Raspberry Pi IP address')
    parser.add_argument('--pi-user', default='pi', help='Pi username (default: pi)')
    parser.add_argument('--pi-password', help='Pi password')
    parser.add_argument('--pi-key', help='Path to SSH private key')
    parser.add_argument('--skip-install', action='store_true', help='Skip library installation')
    parser.add_argument('--skip-diagnostic', action='store_true', help='Skip diagnostic check')
    
    args = parser.parse_args()
    
    # Create setup instance
    setup = PiSetup(
        pi_host=args.pi_host,
        pi_user=args.pi_user,
        pi_password=args.pi_password,
        pi_key_path=args.pi_key
    )
    
    try:
        # Connect to Pi
        if not setup.connect():
            sys.exit(1)
        
        # Deploy files
        if not setup.deploy_files():
            print("❌ File deployment failed")
            sys.exit(1)
        
        # Install libraries (unless skipped)
        if not args.skip_install:
            if not setup.install_libraries():
                print("❌ Library installation failed")
                sys.exit(1)
        
        # Run diagnostic (unless skipped)
        if not args.skip_diagnostic:
            setup.run_diagnostic()
        
        # Check streaming service
        setup.check_streaming_service()
        
        print("\n" + "="*60)
        print("🎯 SETUP COMPLETE!")
        print("="*60)
        print("Next steps:")
        print("1. Connect your Kinect to the Pi")
        print("2. SSH to your Pi and run:")
        print("   cd kinect_diagnostic")
        print("   python3 kinect_unified_streamer.py")
        print(f"3. Open http://{args.pi_host}:8080 in your browser")
        
    except KeyboardInterrupt:
        print("\n⏹️ Operation cancelled by user")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    finally:
        setup.disconnect()

if __name__ == '__main__':
    main()
