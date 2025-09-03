#!/usr/bin/env python3
"""
Deploy diagnostic tools to Raspberry Pi
"""

import paramiko
import os
import sys
import time

def deploy_files_to_pi(pi_host, pi_user="pi", pi_password=None, pi_key_path=None):
    """Deploy diagnostic files to Raspberry Pi"""
    
    print(f"🚀 Deploying diagnostic tools to Raspberry Pi at {pi_host}...")
    
    # Files to deploy
    files_to_deploy = [
        "check_pi_libraries.py",
        "install_pi_libraries.sh"
    ]
    
    ssh_client = None
    
    try:
        # Connect to Pi
        print("🔌 Connecting to Raspberry Pi...")
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        if pi_key_path and os.path.exists(pi_key_path):
            print(f"🔑 Using SSH key: {pi_key_path}")
            ssh_client.connect(
                hostname=pi_host,
                username=pi_user,
                key_filename=pi_key_path,
                timeout=10
            )
        elif pi_password:
            print("🔑 Using password authentication")
            ssh_client.connect(
                hostname=pi_host,
                username=pi_user,
                password=pi_password,
                timeout=10
            )
        else:
            print("❌ No authentication method provided")
            return False
        
        print("✅ Connected to Raspberry Pi successfully")
        
        # Create directory on Pi
        sftp = ssh_client.open_sftp()
        try:
            sftp.mkdir(f"/home/{pi_user}/kinect_diagnostic")
        except:
            pass  # Directory might already exist
        
        # Upload files
        for filename in files_to_deploy:
            if os.path.exists(filename):
                print(f"📤 Uploading {filename}...")
                remote_path = f"/home/{pi_user}/kinect_diagnostic/{filename}"
                sftp.put(filename, remote_path)
                
                # Make executable if it's a shell script
                if filename.endswith('.sh'):
                    stdin, stdout, stderr = ssh_client.exec_command(f"chmod +x {remote_path}")
                    stdout.channel.recv_exit_status()
                    print(f"✅ Made {filename} executable")
                
                print(f"✅ {filename} uploaded successfully")
            else:
                print(f"❌ {filename} not found locally")
        
        sftp.close()
        
        print("\n🎯 Deployment complete!")
        print(f"Files deployed to: /home/{pi_user}/kinect_diagnostic/")
        print("\nNext steps:")
        print(f"1. SSH to your Pi: ssh {pi_user}@{pi_host}")
        print("2. Run: cd kinect_diagnostic")
        print("3. Run: bash install_pi_libraries.sh")
        print("4. Run: python3 check_pi_libraries.py")
        
        return True
        
    except Exception as e:
        print(f"❌ Deployment failed: {e}")
        return False
    finally:
        if ssh_client:
            ssh_client.close()

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Deploy diagnostic tools to Raspberry Pi')
    parser.add_argument('--pi-host', required=True, help='Raspberry Pi IP address')
    parser.add_argument('--pi-user', default='pi', help='Pi username (default: pi)')
    parser.add_argument('--pi-password', help='Pi password')
    parser.add_argument('--pi-key', help='Path to SSH private key')
    
    args = parser.parse_args()
    
    success = deploy_files_to_pi(
        pi_host=args.pi_host,
        pi_user=args.pi_user,
        pi_password=args.pi_password,
        pi_key_path=args.pi_key
    )
    
    if success:
        print("\n✅ Deployment successful!")
    else:
        print("\n❌ Deployment failed!")
        sys.exit(1)

if __name__ == '__main__':
    main()
