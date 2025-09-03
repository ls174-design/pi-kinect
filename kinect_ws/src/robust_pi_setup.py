#!/usr/bin/env python3
"""
Robust Raspberry Pi setup with better SSH handling
"""

import paramiko
import os
import sys
import time
import socket

class RobustPiSetup:
    def __init__(self, pi_host, pi_user="pi", pi_password=None, pi_key_path=None):
        self.pi_host = pi_host
        self.pi_user = pi_user
        self.pi_password = pi_password
        self.pi_key_path = pi_key_path
        self.ssh_client = None
        
    def test_connection(self):
        """Test basic connectivity before attempting SSH"""
        print(f"🌐 Testing connectivity to {self.pi_host}...")
        
        # Test ping
        try:
            import subprocess
            result = subprocess.run(['ping', '-n', '1', self.pi_host], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode != 0:
                print(f"❌ Cannot ping {self.pi_host}")
                return False
            print(f"✅ Ping to {self.pi_host} successful")
        except Exception as e:
            print(f"❌ Ping test failed: {e}")
            return False
        
        # Test SSH port
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((self.pi_host, 22))
            sock.close()
            
            if result != 0:
                print(f"❌ SSH port 22 is not open on {self.pi_host}")
                return False
            print(f"✅ SSH port 22 is open on {self.pi_host}")
        except Exception as e:
            print(f"❌ SSH port test failed: {e}")
            return False
        
        return True
        
    def connect_with_retry(self, max_retries=3):
        """Connect to Pi with multiple retry attempts and different methods"""
        print(f"🔌 Connecting to Raspberry Pi at {self.pi_host}...")
        
        for attempt in range(max_retries):
            print(f"Attempt {attempt + 1}/{max_retries}")
            
            # Try different connection methods
            methods = []
            
            if self.pi_password:
                methods.append(('password', self.pi_password))
            
            if self.pi_key_path and os.path.exists(self.pi_key_path):
                methods.append(('key', self.pi_key_path))
            
            # Try common SSH key locations
            common_keys = [
                os.path.expanduser("~/.ssh/id_rsa"),
                os.path.expanduser("~/.ssh/id_ed25519"),
                os.path.expanduser("~/.ssh/id_ecdsa"),
            ]
            
            for key_path in common_keys:
                if os.path.exists(key_path):
                    methods.append(('key', key_path))
            
            for method_type, method_value in methods:
                try:
                    print(f"  Trying {method_type} authentication...")
                    
                    self.ssh_client = paramiko.SSHClient()
                    self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                    
                    if method_type == 'password':
                        self.ssh_client.connect(
                            hostname=self.pi_host,
                            username=self.pi_user,
                            password=method_value,
                            timeout=15,
                            allow_agent=False,
                            look_for_keys=False
                        )
                    else:  # key
                        self.ssh_client.connect(
                            hostname=self.pi_host,
                            username=self.pi_user,
                            key_filename=method_value,
                            timeout=15,
                            allow_agent=False,
                            look_for_keys=False
                        )
                    
                    # Test the connection
                    stdin, stdout, stderr = self.ssh_client.exec_command("echo 'Connection test successful'")
                    output = stdout.read().decode('utf-8').strip()
                    
                    if "Connection test successful" in output:
                        print(f"✅ Connected successfully using {method_type} authentication")
                        return True
                    
                except paramiko.AuthenticationException:
                    print(f"  ❌ Authentication failed with {method_type}")
                except paramiko.SSHException as e:
                    print(f"  ⚠️ SSH error with {method_type}: {e}")
                except Exception as e:
                    print(f"  ⚠️ Connection error with {method_type}: {e}")
                finally:
                    if self.ssh_client:
                        self.ssh_client.close()
                        self.ssh_client = None
            
            if attempt < max_retries - 1:
                print(f"  Waiting 5 seconds before retry...")
                time.sleep(5)
        
        print("❌ All connection attempts failed")
        return False
    
    def connect(self):
        """Main connection method"""
        if not self.test_connection():
            return False
        
        return self.connect_with_retry()
    
    def run_command(self, command, timeout=60):
        """Run a command on the Pi and return output"""
        try:
            if not self.ssh_client:
                return False, "", "No SSH connection available"
            
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
            if not self.ssh_client:
                print(f"❌ No SSH connection available for upload")
                return False
            
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
    
    def disconnect(self):
        """Disconnect from the Pi"""
        if self.ssh_client:
            self.ssh_client.close()
            print("🔌 Disconnected from Raspberry Pi")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Robust Pi setup with better SSH handling')
    parser.add_argument('--pi-host', required=True, help='Raspberry Pi IP address')
    parser.add_argument('--pi-user', default='pi', help='Pi username (default: pi)')
    parser.add_argument('--pi-password', help='Pi password')
    parser.add_argument('--pi-key', help='Path to SSH private key')
    parser.add_argument('--skip-install', action='store_true', help='Skip library installation')
    parser.add_argument('--skip-diagnostic', action='store_true', help='Skip diagnostic check')
    
    args = parser.parse_args()
    
    # Create setup instance
    setup = RobustPiSetup(
        pi_host=args.pi_host,
        pi_user=args.pi_user,
        pi_password=args.pi_password,
        pi_key_path=args.pi_key
    )
    
    try:
        # Connect to Pi
        if not setup.connect():
            print("\n❌ Could not connect to Raspberry Pi")
            print("\nTroubleshooting suggestions:")
            print("1. Verify Pi IP address and username")
            print("2. Check if SSH is enabled on Pi")
            print("3. Try running: ssh_troubleshoot.bat")
            print("4. Verify password (default is often 'raspberry')")
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
