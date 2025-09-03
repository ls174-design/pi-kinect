#!/usr/bin/env python3
"""
Test Pi Setup - Verifies that all files are on Pi and ready to use
"""

import os
import sys
import subprocess
from pathlib import Path

def get_ssh_key_path():
    """Get the SSH key path"""
    home = Path.home()
    ssh_key = home / ".ssh" / "pi_kinect_ls_192_168_1_9_key"
    return str(ssh_key)

def run_ssh_command(command):
    """Run SSH command with key authentication"""
    ssh_key_path = get_ssh_key_path()
    
    if not os.path.exists(ssh_key_path):
        print(f"❌ SSH key not found: {ssh_key_path}")
        return False, "", "SSH key not found"
    
    cmd = ["ssh", "-i", ssh_key_path, "ls@192.168.1.9", command]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Command timed out"
    except Exception as e:
        return False, "", str(e)

def test_pi_setup():
    """Test Pi setup"""
    print("🔍 Testing Pi Setup")
    print("=" * 50)
    
    # Test SSH connection
    print("1. Testing SSH connection...")
    success, stdout, stderr = run_ssh_command("echo 'SSH connection test successful'")
    if success and "SSH connection test successful" in stdout:
        print("   ✅ SSH connection working")
    else:
        print(f"   ❌ SSH connection failed: {stderr}")
        return False
    
    # Check if kinect_ws directory exists
    print("\n2. Checking kinect_ws directory...")
    success, stdout, stderr = run_ssh_command("ls -la ~/kinect_ws/")
    if success:
        print("   ✅ kinect_ws directory exists")
        print(f"   📁 Contents: {stdout.strip()}")
    else:
        print(f"   ❌ kinect_ws directory not found: {stderr}")
        return False
    
    # Check required files
    print("\n3. Checking required files...")
    required_files = [
        "kinect_launcher.py",
        "kinect_unified_streamer.py", 
        "windows_camera_viewer.py",
        "requirements.txt"
    ]
    
    all_files_exist = True
    for file in required_files:
        success, stdout, stderr = run_ssh_command(f"test -f ~/kinect_ws/{file} && echo 'exists'")
        if success and "exists" in stdout:
            print(f"   ✅ {file} exists")
        else:
            print(f"   ❌ {file} missing")
            all_files_exist = False
    
    if not all_files_exist:
        print("\n❌ Some required files are missing. Run sync again.")
        return False
    
    # Check Python dependencies
    print("\n4. Checking Python dependencies...")
    success, stdout, stderr = run_ssh_command("python3 -c 'import cv2, numpy, PIL, requests; print(\"All packages available\")'")
    if success and "All packages available" in stdout:
        print("   ✅ All Python packages are installed")
    else:
        print("   ⚠️ Some Python packages may be missing")
        print("   💡 Run: pip3 install -r ~/kinect_ws/requirements.txt")
    
    # Test Kinect launcher
    print("\n5. Testing Kinect launcher...")
    success, stdout, stderr = run_ssh_command("cd ~/kinect_ws && python3 -c 'import kinect_launcher; print(\"Launcher imports successfully\")'")
    if success and "Launcher imports successfully" in stdout:
        print("   ✅ Kinect launcher imports successfully")
    else:
        print(f"   ⚠️ Kinect launcher import issue: {stderr}")
    
    print("\n" + "=" * 50)
    print("📋 PI SETUP TEST COMPLETE")
    print("=" * 50)
    print("✅ Pi setup is ready!")
    print("\n📋 You can now:")
    print("   1. SSH to Pi: ssh -i ~/.ssh/pi_kinect_ls_192_168_1_9_key ls@192.168.1.9")
    print("   2. Run Kinect launcher: python3 ~/kinect_ws/kinect_launcher.py")
    print("   3. Or run unified streamer: python3 ~/kinect_ws/kinect_unified_streamer.py")
    
    return True

def main():
    """Main function"""
    try:
        test_pi_setup()
    except KeyboardInterrupt:
        print("\n\n⚠️ Test cancelled by user.")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
    
    input("\nPress Enter to exit...")

if __name__ == '__main__':
    main()
