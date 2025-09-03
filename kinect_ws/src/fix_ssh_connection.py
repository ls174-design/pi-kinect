#!/usr/bin/env python3
"""
SSH Connection Fix Script
This script will help diagnose and fix SSH connection issues
"""

import subprocess
import sys
import os
import getpass

def test_ssh_connection(host, user, use_password=True):
    """Test SSH connection with different methods"""
    print(f"🔍 Testing SSH connection to {user}@{host}")
    print("="*50)
    
    # Test 1: Basic connectivity
    print("1. Testing basic connectivity...")
    try:
        result = subprocess.run(f"ping -c 1 {host}", shell=True, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ Host is reachable")
        else:
            print("❌ Host is not reachable")
            return False
    except Exception as e:
        print(f"❌ Ping test failed: {e}")
        return False
    
    # Test 2: SSH port connectivity
    print("\n2. Testing SSH port (22)...")
    try:
        result = subprocess.run(f"nc -z -v {host} 22", shell=True, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ SSH port 22 is open")
        else:
            print("❌ SSH port 22 is not accessible")
            print("   Try: telnet {host} 22")
            return False
    except Exception as e:
        print(f"❌ Port test failed: {e}")
        return False
    
    # Test 3: SSH connection with verbose output
    print("\n3. Testing SSH connection (verbose)...")
    ssh_cmd = f"ssh -v -o ConnectTimeout=10 -o BatchMode=no {user}@{host} 'echo SSH connection successful'"
    
    if use_password:
        print("   This will prompt for password...")
        try:
            result = subprocess.run(ssh_cmd, shell=True, timeout=30)
            if result.returncode == 0:
                print("✅ SSH connection successful")
                return True
            else:
                print("❌ SSH connection failed")
                return False
        except subprocess.TimeoutExpired:
            print("⏰ SSH connection timed out")
            return False
        except Exception as e:
            print(f"❌ SSH connection error: {e}")
            return False
    else:
        print("   Testing with key authentication...")
        try:
            result = subprocess.run(ssh_cmd, shell=True, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                print("✅ SSH connection successful")
                return True
            else:
                print("❌ SSH connection failed")
                print(f"   Error: {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ SSH connection error: {e}")
            return False

def generate_ssh_config():
    """Generate SSH config for easier connection"""
    print("\n🔧 Generating SSH config...")
    
    config_content = """# SSH config for Pi connection
Host pi
    HostName 192.168.1.9
    User ls
    Port 22
    PreferredAuthentications password
    PubkeyAuthentication no
    PasswordAuthentication yes
    StrictHostKeyChecking no
    UserKnownHostsFile /dev/null
"""
    
    ssh_dir = os.path.expanduser("~/.ssh")
    config_file = os.path.join(ssh_dir, "config")
    
    # Create .ssh directory if it doesn't exist
    os.makedirs(ssh_dir, exist_ok=True)
    
    # Write config file
    with open(config_file, "w") as f:
        f.write(config_content)
    
    # Set proper permissions
    os.chmod(config_file, 0o600)
    os.chmod(ssh_dir, 0o700)
    
    print(f"✅ SSH config written to {config_file}")
    print("   You can now use: ssh pi")

def create_ssh_scripts():
    """Create convenient SSH scripts"""
    print("\n📝 Creating SSH helper scripts...")
    
    # Windows batch script
    batch_content = """@echo off
echo Connecting to Pi...
ssh -o PreferredAuthentications=password -o PubkeyAuthentication=no ls@192.168.1.9
pause
"""
    
    with open("connect_to_pi.bat", "w") as f:
        f.write(batch_content)
    
    # PowerShell script
    ps_content = """# PowerShell script to connect to Pi
Write-Host "Connecting to Pi..." -ForegroundColor Green
ssh -o PreferredAuthentications=password -o PubkeyAuthentication=no ls@192.168.1.9
"""
    
    with open("connect_to_pi.ps1", "w") as f:
        f.write(ps_content)
    
    print("✅ Created connect_to_pi.bat and connect_to_pi.ps1")

def test_alternative_methods(host, user):
    """Test alternative connection methods"""
    print("\n🔄 Testing alternative connection methods...")
    
    methods = [
        {
            "name": "SSH with password auth only",
            "cmd": f"ssh -o PreferredAuthentications=password -o PubkeyAuthentication=no -o ConnectTimeout=10 {user}@{host} 'echo test'"
        },
        {
            "name": "SSH with no host key checking",
            "cmd": f"ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout=10 {user}@{host} 'echo test'"
        },
        {
            "name": "SSH with all options",
            "cmd": f"ssh -o PreferredAuthentications=password -o PubkeyAuthentication=no -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout=10 {user}@{host} 'echo test'"
        }
    ]
    
    for method in methods:
        print(f"\n   Testing: {method['name']}")
        try:
            result = subprocess.run(method['cmd'], shell=True, capture_output=True, text=True, timeout=15)
            if result.returncode == 0:
                print(f"   ✅ {method['name']}: SUCCESS")
                return method['cmd']
            else:
                print(f"   ❌ {method['name']}: FAILED")
                if result.stderr:
                    print(f"      Error: {result.stderr.strip()}")
        except subprocess.TimeoutExpired:
            print(f"   ⏰ {method['name']}: TIMEOUT")
        except Exception as e:
            print(f"   ❌ {method['name']}: ERROR - {e}")
    
    return None

def main():
    """Main SSH fix function"""
    print("🔧 SSH CONNECTION FIX TOOL")
    print("="*50)
    
    host = "192.168.1.9"
    user = "ls"
    
    print(f"Target: {user}@{host}")
    print()
    
    # Test current connection
    print("Testing current SSH connection...")
    success = test_ssh_connection(host, user, use_password=True)
    
    if not success:
        print("\n🔍 Connection failed. Testing alternative methods...")
        working_cmd = test_alternative_methods(host, user)
        
        if working_cmd:
            print(f"\n✅ Found working method!")
            print(f"Working command: {working_cmd}")
        else:
            print("\n❌ All connection methods failed")
            print("\n🔧 TROUBLESHOOTING STEPS:")
            print("1. Check if SSH service is running on Pi:")
            print("   sudo systemctl status ssh")
            print("2. Check SSH configuration on Pi:")
            print("   sudo nano /etc/ssh/sshd_config")
            print("3. Restart SSH service on Pi:")
            print("   sudo systemctl restart ssh")
            print("4. Check firewall on Pi:")
            print("   sudo ufw status")
            print("5. Try connecting from Pi to itself:")
            print("   ssh localhost")
    
    # Generate helper files
    generate_ssh_config()
    create_ssh_scripts()
    
    print("\n📋 NEXT STEPS:")
    print("1. Try the generated scripts:")
    print("   - Double-click connect_to_pi.bat")
    print("   - Or run: ssh pi")
    print("2. If still failing, check Pi SSH service:")
    print("   - SSH might be disabled")
    print("   - Firewall might be blocking")
    print("   - User might not exist")
    
    print("\n" + "="*50)
    print("SSH FIX COMPLETE")

if __name__ == "__main__":
    main()
