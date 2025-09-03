#!/usr/bin/env python3
"""
Simple File Transfer to Raspberry Pi
Just uploads the diagnostic files without complex setup
"""

import paramiko
import os
import sys

def upload_files_to_pi(pi_host, pi_user, pi_password):
    """Simple file upload to Pi"""
    
    print(f"📤 Uploading files to {pi_user}@{pi_host}...")
    
    ssh_client = None
    try:
        # Connect to Pi
        print("🔌 Connecting to Pi...")
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(
            hostname=pi_host,
            username=pi_user,
            password=pi_password,
            timeout=15
        )
        print("✅ Connected successfully!")
        
        # Create directory
        print("📁 Creating directory...")
        stdin, stdout, stderr = ssh_client.exec_command("mkdir -p kinect_diagnostic")
        stdout.channel.recv_exit_status()
        
        # Upload files
        files_to_upload = [
            "check_pi_libraries.py",
            "install_pi_libraries.sh"
        ]
        
        sftp = ssh_client.open_sftp()
        
        for filename in files_to_upload:
            if os.path.exists(filename):
                print(f"📤 Uploading {filename}...")
                remote_path = f"kinect_diagnostic/{filename}"
                sftp.put(filename, remote_path)
                print(f"✅ {filename} uploaded")
            else:
                print(f"❌ {filename} not found locally")
        
        sftp.close()
        
        # Make install script executable
        print("🔧 Making install script executable...")
        stdin, stdout, stderr = ssh_client.exec_command("chmod +x kinect_diagnostic/install_pi_libraries.sh")
        stdout.channel.recv_exit_status()
        
        print("\n✅ File upload complete!")
        print(f"Files uploaded to: /home/{pi_user}/kinect_diagnostic/")
        print("\nNext steps:")
        print("1. SSH to your Pi: ssh pi@192.168.1.9")
        print("2. Run: cd kinect_diagnostic")
        print("3. Run: bash install_pi_libraries.sh")
        print("4. Run: python3 check_pi_libraries.py")
        
        return True
        
    except Exception as e:
        print(f"❌ Upload failed: {e}")
        return False
    finally:
        if ssh_client:
            ssh_client.close()

def main():
    print("📤 Simple File Transfer to Raspberry Pi")
    print("=" * 50)
    
    pi_host = input("Enter Pi IP address: ").strip()
    pi_user = input("Enter Pi username (default: pi): ").strip() or "pi"
    pi_password = input("Enter Pi password: ").strip()
    
    success = upload_files_to_pi(pi_host, pi_user, pi_password)
    
    if success:
        print("\n🎯 File transfer successful!")
    else:
        print("\n❌ File transfer failed!")
        sys.exit(1)

if __name__ == '__main__':
    main()
