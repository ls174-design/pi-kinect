#!/usr/bin/env python3
"""
Smart Sync Tool - Syncs files to Pi using SSH key authentication
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

def run_ssh_command(command, use_key=True):
    """Run SSH command with or without key"""
    ssh_key_path = get_ssh_key_path()
    
    if use_key and os.path.exists(ssh_key_path):
        cmd = ["ssh", "-i", ssh_key_path, "ls@192.168.1.9", command]
    else:
        cmd = ["ssh", "ls@192.168.1.9", command]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Command timed out"
    except Exception as e:
        return False, "", str(e)

def run_scp_command(local_file, remote_path, use_key=True):
    """Run SCP command with or without key"""
    ssh_key_path = get_ssh_key_path()
    
    if use_key and os.path.exists(ssh_key_path):
        cmd = ["scp", "-i", ssh_key_path, local_file, f"ls@192.168.1.9:{remote_path}"]
    else:
        cmd = ["scp", local_file, f"ls@192.168.1.9:{remote_path}"]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Command timed out"
    except Exception as e:
        return False, "", str(e)

def sync_files():
    """Sync files to Pi"""
    print("🔄 Smart Sync to Pi")
    print("=" * 50)
    
    # Check if SSH key exists
    ssh_key_path = get_ssh_key_path()
    use_key = os.path.exists(ssh_key_path)
    
    if use_key:
        print(f"✅ Using SSH key: {ssh_key_path}")
    else:
        print("⚠️ SSH key not found, will use password authentication")
        print("   Consider running: python fix_ssh_auth.py")
    
    # Files to sync
    files_to_sync = [
        "camera_streamer.py",
        "kinect_streamer.py", 
        "kinect_unified_streamer.py",
        "kinect_launcher.py",
        "windows_camera_viewer.py",
        "requirements.txt"
    ]
    
    print(f"\n📁 Syncing {len(files_to_sync)} files to Pi...")
    
    # Create directory on Pi
    print("   Creating kinect_ws directory on Pi...")
    success, stdout, stderr = run_ssh_command("mkdir -p ~/kinect_ws", use_key)
    if success:
        print("   ✅ Directory created")
    else:
        print(f"   ⚠️ Directory creation: {stderr}")
    
    # Sync each file
    synced_count = 0
    for file in files_to_sync:
        if os.path.exists(file):
            print(f"   Syncing {file}...")
            success, stdout, stderr = run_scp_command(file, "~/kinect_ws/", use_key)
            if success:
                print(f"   ✅ {file} synced")
                synced_count += 1
            else:
                print(f"   ❌ {file} failed: {stderr}")
        else:
            print(f"   ⚠️ {file} not found, skipping")
    
    # Make scripts executable
    print("\n   Making scripts executable...")
    success, stdout, stderr = run_ssh_command("chmod +x ~/kinect_ws/*.py", use_key)
    if success:
        print("   ✅ Scripts made executable")
    else:
        print(f"   ⚠️ chmod failed: {stderr}")
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 SYNC SUMMARY")
    print("=" * 50)
    print(f"✅ Successfully synced {synced_count}/{len(files_to_sync)} files")
    
    if synced_count == len(files_to_sync):
        print("\n🎉 All files synced successfully!")
        print("\n📋 Next steps:")
        print("   1. SSH to Pi: ssh -i ~/.ssh/pi_kinect_ls_192_168_1_9_key ls@192.168.1.9")
        print("   2. Install dependencies: pip3 install -r ~/kinect_ws/requirements.txt")
        print("   3. Run Kinect launcher: python3 ~/kinect_ws/kinect_launcher.py")
        print("   4. Or run unified streamer: python3 ~/kinect_ws/kinect_unified_streamer.py")
    else:
        print(f"\n⚠️ {len(files_to_sync) - synced_count} files failed to sync")
        print("   Check your Pi connection and try again")

def main():
    """Main function"""
    try:
        sync_files()
    except KeyboardInterrupt:
        print("\n\n⚠️ Sync cancelled by user.")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
    
    input("\nPress Enter to exit...")

if __name__ == '__main__':
    main()
