#!/usr/bin/env python3
"""
Simple script to copy setup files to Raspberry Pi
"""

import paramiko
import os
import sys

def copy_files_to_pi(pi_host, pi_user, pi_password):
    """Copy setup files to Pi"""
    
    print(f"📤 Copying setup files to {pi_user}@{pi_host}...")
    
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
        stdin, stdout, stderr = ssh_client.exec_command("mkdir -p kinect_setup")
        stdout.channel.recv_exit_status()
        
        # Copy files
        files_to_copy = [
            "setup_on_pi.sh",
            "check_libraries_on_pi.sh",
            "check_pi_libraries.py",
            "install_pi_libraries.sh",
            "complete_pi_setup.sh",
            "install_freenect_from_source.sh",
            "fix_opencv_installation.sh"
        ]
        
        sftp = ssh_client.open_sftp()
        
        for filename in files_to_copy:
            if os.path.exists(filename):
                print(f"📤 Copying {filename}...")
                remote_path = f"kinect_setup/{filename}"
                sftp.put(filename, remote_path)
                print(f"✅ {filename} copied")
            else:
                print(f"❌ {filename} not found locally")
        
        sftp.close()
        
        # Make scripts executable
        print("🔧 Making scripts executable...")
        stdin, stdout, stderr = ssh_client.exec_command("chmod +x kinect_setup/*.sh")
        stdout.channel.recv_exit_status()
        
        print("\n✅ File copy complete!")
        print(f"Files copied to: /home/{pi_user}/kinect_setup/")
        print("\nNext steps on your Pi:")
        print("1. cd kinect_setup")
        print("2. bash setup_on_pi.sh")
        print("3. bash check_libraries_on_pi.sh")
        
        return True
        
    except Exception as e:
        print(f"❌ Copy failed: {e}")
        return False
    finally:
        if ssh_client:
            ssh_client.close()

def main():
    print("📤 Copy Setup Files to Raspberry Pi")
    print("=" * 50)
    
    pi_host = input("Enter Pi IP address: ").strip()
    pi_user = input("Enter Pi username (default: pi): ").strip() or "pi"
    pi_password = input("Enter Pi password: ").strip()
    
    success = copy_files_to_pi(pi_host, pi_user, pi_password)
    
    if success:
        print("\n🎯 File copy successful!")
    else:
        print("\n❌ File copy failed!")
        sys.exit(1)

if __name__ == '__main__':
    main()
