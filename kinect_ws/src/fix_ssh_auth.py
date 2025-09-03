#!/usr/bin/env python3
"""
Simple SSH Authentication Fix Script
Resolves the "path not found" error and sets up proper SSH authentication
"""

import os
import sys
import subprocess
import tempfile
from pathlib import Path

def fix_ssh_authentication():
    """Fix SSH authentication issues"""
    print("🔧 SSH Authentication Fix Tool")
    print("=" * 50)
    
    # Get Pi details
    pi_ip = input("Enter your Pi IP address (default: 192.168.1.9): ").strip()
    if not pi_ip:
        pi_ip = "192.168.1.9"
    
    pi_user = input("Enter your Pi username (default: ls): ").strip()
    if not pi_user:
        pi_user = "ls"
    
    print(f"\n🔍 Fixing SSH authentication for {pi_user}@{pi_ip}")
    
    # Step 1: Check if SSH key exists
    home = Path.home()
    ssh_dir = home / ".ssh"
    ssh_dir.mkdir(exist_ok=True)
    
    key_name = f"pi_kinect_{pi_user}_{pi_ip.replace('.', '_')}_key"
    key_path = ssh_dir / key_name
    pub_key_path = ssh_dir / f"{key_name}.pub"
    
    print(f"   Key path: {key_path}")
    
    # Step 2: Generate SSH key if it doesn't exist
    if not key_path.exists():
        print("   Generating new SSH key...")
        try:
            cmd = [
                "ssh-keygen", "-t", "rsa", "-b", "4096",
                "-f", str(key_path),
                "-N", "",  # No passphrase
                "-C", f"pi-kinect-{pi_ip}"
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print("   ✅ SSH key generated successfully")
            else:
                print(f"   ❌ Failed to generate SSH key: {result.stderr}")
                return False
        except Exception as e:
            print(f"   ❌ Error generating SSH key: {e}")
            return False
    else:
        print("   ✅ SSH key already exists")
    
    # Step 3: Deploy public key using multiple methods
    print("   Deploying public key to Pi...")
    
    # Method 1: Try ssh-copy-id
    success = False
    try:
        cmd = ["ssh-copy-id", "-i", str(pub_key_path), f"{pi_user}@{pi_ip}"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print("   ✅ Public key deployed using ssh-copy-id")
            success = True
        else:
            print(f"   ⚠️ ssh-copy-id failed: {result.stderr}")
    except Exception as e:
        print(f"   ⚠️ ssh-copy-id error: {e}")
    
    # Method 2: Try manual deployment if ssh-copy-id failed
    if not success:
        try:
            # Read public key
            with open(pub_key_path, 'r') as f:
                public_key = f.read().strip()
            
            # Create SSH directory on Pi
            ssh_dir_cmd = [
                "ssh", f"{pi_user}@{pi_ip}",
                "mkdir -p ~/.ssh && chmod 700 ~/.ssh"
            ]
            result = subprocess.run(ssh_dir_cmd, capture_output=True, text=True, timeout=15)
            
            if result.returncode == 0:
                # Add public key to authorized_keys
                auth_keys_cmd = [
                    "ssh", f"{pi_user}@{pi_ip}",
                    f"echo '{public_key}' >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys"
                ]
                result = subprocess.run(auth_keys_cmd, capture_output=True, text=True, timeout=15)
                
                if result.returncode == 0:
                    print("   ✅ Public key deployed manually")
                    success = True
                else:
                    print(f"   ❌ Manual deployment failed: {result.stderr}")
            else:
                print(f"   ❌ Failed to create SSH directory: {result.stderr}")
                
        except Exception as e:
            print(f"   ❌ Manual deployment error: {e}")
    
    # Method 3: Try temp file method if others failed
    if not success:
        try:
            with open(pub_key_path, 'r') as f:
                public_key = f.read().strip()
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.pub') as temp_file:
                temp_file.write(public_key)
                temp_file_path = temp_file.name
            
            try:
                # Copy to Pi
                scp_cmd = [
                    "scp", temp_file_path,
                    f"{pi_user}@{pi_ip}:~/.ssh/authorized_keys"
                ]
                result = subprocess.run(scp_cmd, capture_output=True, text=True, timeout=15)
                
                if result.returncode == 0:
                    # Set permissions
                    chmod_cmd = [
                        "ssh", f"{pi_user}@{pi_ip}",
                        "chmod 600 ~/.ssh/authorized_keys"
                    ]
                    subprocess.run(chmod_cmd, capture_output=True, text=True, timeout=10)
                    print("   ✅ Public key deployed using temp file method")
                    success = True
                else:
                    print(f"   ❌ Temp file deployment failed: {result.stderr}")
                    
            finally:
                # Clean up temp file
                try:
                    os.unlink(temp_file_path)
                except:
                    pass
                    
        except Exception as e:
            print(f"   ❌ Temp file deployment error: {e}")
    
    if not success:
        print("\n❌ All deployment methods failed!")
        print("   Try running this command manually:")
        print(f"   ssh-copy-id -i {pub_key_path} {pi_user}@{pi_ip}")
        return False
    
    # Step 4: Test authentication
    print("   Testing SSH authentication...")
    try:
        cmd = [
            "ssh", "-i", str(key_path),
            "-o", "PasswordAuthentication=no",
            "-o", "ConnectTimeout=10",
            f"{pi_user}@{pi_ip}",
            "echo 'SSH authentication test successful'"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        
        if result.returncode == 0 and "SSH authentication test successful" in result.stdout:
            print("   ✅ SSH authentication test passed!")
            print("\n🎉 SSH authentication setup complete!")
            print(f"   You can now connect using: ssh -i {key_path} {pi_user}@{pi_ip}")
            return True
        else:
            print(f"   ❌ SSH authentication test failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"   ❌ SSH authentication test error: {e}")
        return False

def main():
    """Main function"""
    try:
        success = fix_ssh_authentication()
        if success:
            print("\n✅ SSH authentication is now working!")
            print("   You can now use the camera launcher without password prompts.")
        else:
            print("\n❌ SSH authentication setup failed.")
            print("   You may need to set it up manually or check your Pi connection.")
    except KeyboardInterrupt:
        print("\n\n⚠️ Setup cancelled by user.")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
    
    input("\nPress Enter to exit...")

if __name__ == '__main__':
    main()
