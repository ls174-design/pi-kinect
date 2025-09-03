#!/usr/bin/env python3
"""
Manual Raspberry Pi Setup - Step by Step
This script guides you through the setup process manually
"""

import paramiko
import os
import sys
import time
import socket
import subprocess

def test_network_connectivity(pi_host):
    """Test basic network connectivity to Pi"""
    print(f"🌐 Testing connectivity to {pi_host}...")
    
    # Test ping
    try:
        result = subprocess.run(['ping', '-n', '1', pi_host], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode != 0:
            print(f"❌ Cannot ping {pi_host}")
            return False
        print(f"✅ Ping to {pi_host} successful")
    except Exception as e:
        print(f"❌ Ping test failed: {e}")
        return False
    
    # Test SSH port
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((pi_host, 22))
        sock.close()
        
        if result != 0:
            print(f"❌ SSH port 22 is not open on {pi_host}")
            return False
        print(f"✅ SSH port 22 is open on {pi_host}")
    except Exception as e:
        print(f"❌ SSH port test failed: {e}")
        return False
    
    return True

def test_ssh_connection(pi_host, pi_user, pi_password):
    """Test SSH connection with detailed error reporting"""
    print(f"🔌 Testing SSH connection to {pi_user}@{pi_host}...")
    
    ssh_client = None
    try:
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        print("  Attempting connection...")
        ssh_client.connect(
            hostname=pi_host,
            username=pi_user,
            password=pi_password,
            timeout=15,
            allow_agent=False,
            look_for_keys=False
        )
        
        print("  Testing command execution...")
        stdin, stdout, stderr = ssh_client.exec_command("echo 'SSH test successful'")
        output = stdout.read().decode('utf-8').strip()
        
        if "SSH test successful" in output:
            print("✅ SSH connection successful!")
            return True, ssh_client
        else:
            print("❌ SSH connection failed - command test failed")
            return False, None
            
    except paramiko.AuthenticationException:
        print("❌ SSH authentication failed - check username/password")
        return False, None
    except paramiko.SSHException as e:
        print(f"❌ SSH error: {e}")
        return False, None
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False, None
    finally:
        if ssh_client and not "SSH test successful" in output:
            ssh_client.close()

def upload_file_safe(ssh_client, local_path, remote_path):
    """Safely upload a file with error checking"""
    try:
        if not ssh_client:
            print(f"❌ No SSH connection for upload")
            return False
        
        if not os.path.exists(local_path):
            print(f"❌ Local file not found: {local_path}")
            return False
        
        print(f"📤 Uploading {local_path} to {remote_path}...")
        sftp = ssh_client.open_sftp()
        sftp.put(local_path, remote_path)
        sftp.close()
        print(f"✅ {local_path} uploaded successfully")
        return True
        
    except Exception as e:
        print(f"❌ Upload failed: {e}")
        return False

def run_command_safe(ssh_client, command, timeout=60):
    """Safely run a command with error checking"""
    try:
        if not ssh_client:
            return False, "", "No SSH connection"
        
        print(f"🔧 Running: {command}")
        stdin, stdout, stderr = ssh_client.exec_command(command, timeout=timeout)
        
        # Wait for command to complete
        exit_status = stdout.channel.recv_exit_status()
        
        output = stdout.read().decode('utf-8')
        error = stderr.read().decode('utf-8')
        
        if exit_status == 0:
            print(f"✅ Command completed successfully")
        else:
            print(f"⚠️ Command completed with exit code {exit_status}")
        
        return exit_status == 0, output, error
        
    except Exception as e:
        print(f"❌ Command failed: {e}")
        return False, "", str(e)

def main():
    print("🔧 Manual Raspberry Pi Setup")
    print("=" * 50)
    
    # Get connection details
    pi_host = input("Enter Raspberry Pi IP address: ").strip()
    pi_user = input("Enter Pi username (default: pi): ").strip() or "pi"
    pi_password = input("Enter Pi password: ").strip()
    
    print(f"\nTarget: {pi_user}@{pi_host}")
    print("=" * 50)
    
    # Step 1: Test network connectivity
    print("\n📡 Step 1: Testing network connectivity...")
    if not test_network_connectivity(pi_host):
        print("\n❌ Network connectivity failed!")
        print("Please check:")
        print("1. Pi IP address is correct")
        print("2. Pi is powered on and connected to network")
        print("3. Both devices are on the same network")
        return False
    
    # Step 2: Test SSH connection
    print("\n🔑 Step 2: Testing SSH connection...")
    success, ssh_client = test_ssh_connection(pi_host, pi_user, pi_password)
    if not success:
        print("\n❌ SSH connection failed!")
        print("Please check:")
        print("1. SSH is enabled on Pi: sudo systemctl enable ssh")
        print("2. SSH service is running: sudo systemctl start ssh")
        print("3. Username and password are correct")
        print("4. Password authentication is enabled in /etc/ssh/sshd_config")
        return False
    
    try:
        # Step 3: Create directory
        print("\n📁 Step 3: Creating directory on Pi...")
        success, output, error = run_command_safe(ssh_client, "mkdir -p kinect_diagnostic")
        if not success:
            print(f"⚠️ Directory creation warning: {error}")
        
        # Step 4: Upload files
        print("\n📤 Step 4: Uploading diagnostic files...")
        files_to_upload = [
            ("check_pi_libraries.py", "kinect_diagnostic/check_pi_libraries.py"),
            ("install_pi_libraries.sh", "kinect_diagnostic/install_pi_libraries.sh")
        ]
        
        upload_success = True
        for local_file, remote_file in files_to_upload:
            if not upload_file_safe(ssh_client, local_file, remote_file):
                upload_success = False
        
        if not upload_success:
            print("\n❌ File upload failed!")
            return False
        
        # Step 5: Make scripts executable
        print("\n🔧 Step 5: Making scripts executable...")
        run_command_safe(ssh_client, "chmod +x kinect_diagnostic/install_pi_libraries.sh")
        
        # Step 6: Ask about installation
        print("\n📦 Step 6: Library installation...")
        install_choice = input("Do you want to install libraries now? (y/n): ").strip().lower()
        
        if install_choice == 'y':
            print("🔧 Installing libraries (this may take 10-15 minutes)...")
            success, output, error = run_command_safe(ssh_client, 
                "cd kinect_diagnostic && bash install_pi_libraries.sh", timeout=900)
            
            if success:
                print("✅ Library installation completed!")
                print("\nInstallation output:")
                print("-" * 40)
                print(output)
                if error:
                    print("\nWarnings/Errors:")
                    print(error)
            else:
                print("❌ Library installation failed!")
                print("Error:", error)
                print("Output:", output)
        
        # Step 7: Run diagnostic
        print("\n🔍 Step 7: Running diagnostic...")
        diag_choice = input("Do you want to run diagnostic check? (y/n): ").strip().lower()
        
        if diag_choice == 'y':
            print("🔍 Running diagnostic check...")
            success, output, error = run_command_safe(ssh_client, 
                "cd kinect_diagnostic && python3 check_pi_libraries.py", timeout=120)
            
            if success:
                print("✅ Diagnostic completed!")
                print("\nDiagnostic output:")
                print("-" * 40)
                print(output)
                if error:
                    print("\nWarnings/Errors:")
                    print(error)
            else:
                print("❌ Diagnostic failed!")
                print("Error:", error)
                print("Output:", output)
        
        print("\n" + "=" * 50)
        print("🎯 SETUP COMPLETE!")
        print("=" * 50)
        print("Next steps:")
        print("1. Connect your Kinect to the Pi")
        print("2. SSH to your Pi and run:")
        print("   cd kinect_diagnostic")
        print("   python3 kinect_unified_streamer.py")
        print(f"3. Open http://{pi_host}:8080 in your browser")
        
        return True
        
    finally:
        if ssh_client:
            ssh_client.close()
            print("\n🔌 Disconnected from Raspberry Pi")

if __name__ == '__main__':
    try:
        success = main()
        if not success:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n⏹️ Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
