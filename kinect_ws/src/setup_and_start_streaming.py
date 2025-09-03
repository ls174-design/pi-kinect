#!/usr/bin/env python3
"""
Complete script to copy streaming script and start the service on Pi
"""

import paramiko
import time
import requests
import sys
import os

def copy_and_start_streaming(pi_host, pi_user, pi_password):
    """Copy streaming script and start the service"""
    
    print(f"🚀 Setting up and starting streaming service on {pi_user}@{pi_host}...")
    
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
        
        # Create kinect_setup directory if it doesn't exist
        print("📁 Creating kinect_setup directory...")
        stdin, stdout, stderr = ssh_client.exec_command("mkdir -p kinect_setup")
        stdout.channel.recv_exit_status()
        
        # Copy the streaming script
        script_file = "kinect_unified_streamer.py"
        if os.path.exists(script_file):
            print(f"📤 Copying {script_file}...")
            sftp = ssh_client.open_sftp()
            remote_path = f"kinect_setup/{script_file}"
            sftp.put(script_file, remote_path)
            sftp.close()
            print(f"✅ {script_file} copied successfully")
            
            # Make the script executable
            print("🔧 Making script executable...")
            stdin, stdout, stderr = ssh_client.exec_command(f"chmod +x kinect_setup/{script_file}")
            stdout.channel.recv_exit_status()
            
        else:
            print(f"❌ {script_file} not found locally")
            return False
        
        # Check if streaming service is already running
        print("🔍 Checking if streaming service is already running...")
        stdin, stdout, stderr = ssh_client.exec_command("pgrep -f kinect_unified_streamer")
        running_processes = stdout.read().decode().strip()
        
        if running_processes:
            print(f"⚠️ Streaming service already running (PID: {running_processes})")
            print("🛑 Stopping existing service...")
            ssh_client.exec_command("pkill -f kinect_unified_streamer")
            time.sleep(2)
        
        # Start the streaming service
        print("📹 Starting Kinect streaming service...")
        start_command = "cd kinect_setup && nohup python3 kinect_unified_streamer.py > streaming.log 2>&1 &"
        stdin, stdout, stderr = ssh_client.exec_command(start_command)
        
        # Wait a moment for the service to start
        time.sleep(3)
        
        # Check if the service started successfully
        print("🧪 Testing streaming service...")
        stdin, stdout, stderr = ssh_client.exec_command("pgrep -f kinect_unified_streamer")
        new_processes = stdout.read().decode().strip()
        
        if new_processes:
            print(f"✅ Streaming service started successfully (PID: {new_processes})")
            
            # Test the HTTP endpoint
            print("🌐 Testing HTTP endpoint...")
            try:
                response = requests.get(f'http://{pi_host}:8080/status', timeout=10)
                if response.status_code == 200:
                    print("✅ HTTP endpoint responding correctly")
                    status = response.json()
                    print(f"📊 Service status: {status}")
                    return True
                else:
                    print(f"⚠️ HTTP endpoint returned status code: {response.status_code}")
            except requests.exceptions.RequestException as e:
                print(f"⚠️ HTTP endpoint test failed: {e}")
                print("💡 Service might still be starting up...")
            
            return True
        else:
            print("❌ Failed to start streaming service")
            
            # Check the log for errors
            print("📋 Checking startup log...")
            stdin, stdout, stderr = ssh_client.exec_command("cd kinect_setup && tail -20 streaming.log")
            log_output = stdout.read().decode().strip()
            if log_output:
                print("📄 Recent log entries:")
                print(log_output)
            
            return False
        
    except Exception as e:
        print(f"❌ Failed to setup streaming service: {e}")
        return False
    finally:
        if ssh_client:
            ssh_client.close()

def main():
    print("🚀 Setup and Start Pi Streaming Service")
    print("=" * 50)
    
    pi_host = input("Enter Pi IP address (default: 192.168.1.9): ").strip() or "192.168.1.9"
    pi_user = input("Enter Pi username (default: ls): ").strip() or "ls"
    pi_password = input("Enter Pi password: ").strip()
    
    if not pi_password:
        print("❌ Password is required")
        sys.exit(1)
    
    success = copy_and_start_streaming(pi_host, pi_user, pi_password)
    
    if success:
        print("\n🎉 Streaming service setup and started successfully!")
        print(f"📺 You can now view the stream at: http://{pi_host}:8080")
        print("💡 Use the Windows camera viewer to connect")
    else:
        print("\n❌ Failed to setup streaming service")
        print("💡 Check the Pi setup and try running the diagnostic scripts")
        sys.exit(1)

if __name__ == '__main__':
    main()
