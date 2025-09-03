#!/usr/bin/env python3
"""
SSH Diagnostic Tool
Identifies SSH authentication issues and provides solutions
"""

import os
import sys
import subprocess
from pathlib import Path

def check_ssh_installation():
    """Check if SSH tools are installed"""
    print("🔍 Checking SSH Installation...")
    
    tools = ['ssh', 'ssh-keygen', 'ssh-copy-id', 'scp']
    for tool in tools:
        try:
            result = subprocess.run([tool, '-V'], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"   ✅ {tool} is installed")
            else:
                print(f"   ⚠️ {tool} is installed but may have issues")
        except FileNotFoundError:
            print(f"   ❌ {tool} is not installed or not in PATH")
            return False
    return True

def check_ssh_directory():
    """Check SSH directory and permissions"""
    print("\n🔍 Checking SSH Directory...")
    
    home = Path.home()
    ssh_dir = home / ".ssh"
    
    if not ssh_dir.exists():
        print(f"   ❌ SSH directory does not exist: {ssh_dir}")
        try:
            ssh_dir.mkdir(mode=0o700)
            print(f"   ✅ Created SSH directory: {ssh_dir}")
        except Exception as e:
            print(f"   ❌ Failed to create SSH directory: {e}")
            return False
    else:
        print(f"   ✅ SSH directory exists: {ssh_dir}")
    
    # Check permissions
    try:
        stat_info = ssh_dir.stat()
        mode = stat_info.st_mode & 0o777
        if mode == 0o700:
            print(f"   ✅ SSH directory permissions are correct: {oct(mode)}")
        else:
            print(f"   ⚠️ SSH directory permissions may be wrong: {oct(mode)} (should be 700)")
    except Exception as e:
        print(f"   ⚠️ Could not check SSH directory permissions: {e}")
    
    return True

def check_existing_keys():
    """Check for existing SSH keys"""
    print("\n🔍 Checking Existing SSH Keys...")
    
    home = Path.home()
    ssh_dir = home / ".ssh"
    
    if not ssh_dir.exists():
        print("   ❌ SSH directory does not exist")
        return []
    
    key_files = []
    for file in ssh_dir.glob("*"):
        if file.is_file() and file.suffix in ['.pub', ''] and 'key' in file.name.lower():
            key_files.append(file)
            print(f"   📁 Found key file: {file.name}")
    
    if not key_files:
        print("   ⚠️ No SSH key files found")
    
    return key_files

def test_pi_connection(pi_ip, pi_user):
    """Test connection to Raspberry Pi"""
    print(f"\n🔍 Testing Connection to {pi_user}@{pi_ip}...")
    
    # Test ping
    try:
        if os.name == 'nt':  # Windows
            cmd = ['ping', '-n', '1', pi_ip]
        else:  # Linux/Mac
            cmd = ['ping', '-c', '1', pi_ip]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"   ✅ Ping to {pi_ip} successful")
        else:
            print(f"   ❌ Ping to {pi_ip} failed")
            return False
    except Exception as e:
        print(f"   ❌ Ping test failed: {e}")
        return False
    
    # Test SSH connection
    try:
        cmd = ['ssh', '-o', 'ConnectTimeout=10', f'{pi_user}@{pi_ip}', 'echo "SSH connection test"']
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        if result.returncode == 0 and "SSH connection test" in result.stdout:
            print(f"   ✅ SSH connection to {pi_user}@{pi_ip} successful")
            return True
        else:
            print(f"   ❌ SSH connection failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"   ❌ SSH connection test failed: {e}")
        return False

def check_ssh_config():
    """Check SSH configuration"""
    print("\n🔍 Checking SSH Configuration...")
    
    home = Path.home()
    ssh_config = home / ".ssh" / "config"
    
    if ssh_config.exists():
        print(f"   ✅ SSH config file exists: {ssh_config}")
        try:
            with open(ssh_config, 'r') as f:
                content = f.read()
                if 'pi' in content.lower() or 'kinect' in content.lower():
                    print("   ✅ SSH config contains Pi/Kinect entries")
                else:
                    print("   ⚠️ SSH config does not contain Pi/Kinect entries")
        except Exception as e:
            print(f"   ⚠️ Could not read SSH config: {e}")
    else:
        print("   ⚠️ SSH config file does not exist")

def main():
    """Main diagnostic function"""
    print("🔧 SSH Diagnostic Tool")
    print("=" * 50)
    
    # Get Pi details
    pi_ip = input("Enter your Pi IP address (default: 192.168.1.9): ").strip()
    if not pi_ip:
        pi_ip = "192.168.1.9"
    
    pi_user = input("Enter your Pi username (default: ls): ").strip()
    if not pi_user:
        pi_user = "ls"
    
    print(f"\n🔍 Running diagnostics for {pi_user}@{pi_ip}")
    
    # Run all checks
    ssh_ok = check_ssh_installation()
    if not ssh_ok:
        print("\n❌ SSH tools are not properly installed!")
        print("   Please install OpenSSH or Git for Windows")
        return
    
    ssh_dir_ok = check_ssh_directory()
    if not ssh_dir_ok:
        print("\n❌ SSH directory issues found!")
        return
    
    existing_keys = check_existing_keys()
    check_ssh_config()
    
    connection_ok = test_pi_connection(pi_ip, pi_user)
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 DIAGNOSTIC SUMMARY")
    print("=" * 50)
    
    if connection_ok:
        print("✅ Basic SSH connection is working")
        if existing_keys:
            print("✅ SSH keys exist")
            print("\n💡 If you're still having authentication issues:")
            print("   1. Run: python fix_ssh_auth.py")
            print("   2. Or manually: ssh-copy-id -i ~/.ssh/your_key.pub ls@192.168.1.9")
        else:
            print("⚠️ No SSH keys found")
            print("\n💡 To fix authentication:")
            print("   1. Run: python fix_ssh_auth.py")
            print("   2. This will generate and deploy SSH keys")
    else:
        print("❌ SSH connection is not working")
        print("\n💡 To fix connection issues:")
        print("   1. Check Pi IP address and username")
        print("   2. Ensure Pi is powered on and connected to network")
        print("   3. Check if SSH service is running on Pi")
        print("   4. Try: ssh ls@192.168.1.9 (should prompt for password)")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Diagnostic cancelled by user.")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
    
    input("\nPress Enter to exit...")
