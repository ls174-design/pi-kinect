#!/usr/bin/env python3
"""
Manual SSH fix script to handle the deployment issue
"""

import os
import sys
import subprocess
import tempfile
from pathlib import Path

def main():
    print("🔧 Manual SSH Authentication Fix")
    print("=" * 50)
    
    pi_host = "192.168.1.9"
    pi_user = "ls"
    
    # Get the SSH key path
    home = Path.home()
    ssh_dir = home / ".ssh"
    ssh_dir.mkdir(exist_ok=True)
    
    key_name = f"pi_kinect_{pi_user}_{pi_host.replace('.', '_')}_key"
    key_path = ssh_dir / key_name
    pub_key_path = ssh_dir / f"{key_name}.pub"
    
    print(f"SSH Key: {key_path}")
    print(f"Public Key: {pub_key_path}")
    
    # Step 1: Check if keys exist
    if not key_path.exists():
        print("❌ Private key not found!")
        return False
    
    if not pub_key_path.exists():
        print("❌ Public key not found!")
        return False
    
    print("✅ SSH keys found")
    
    # Step 2: Read the public key
    try:
        with open(pub_key_path, 'r') as f:
            public_key = f.read().strip()
        print("✅ Public key read successfully")
    except Exception as e:
        print(f"❌ Failed to read public key: {e}")
        return False
    
    # Step 3: Deploy using a different method
    print("\n🔐 Deploying public key to Pi...")
    
    # Method 1: Try using ssh-copy-id if available
    try:
        cmd = f"ssh-copy-id -i {pub_key_path} {pi_user}@{pi_host}"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Public key deployed using ssh-copy-id")
        else:
            print(f"⚠️ ssh-copy-id failed: {result.stderr}")
            raise Exception("ssh-copy-id failed")
    except:
        # Method 2: Manual deployment using SSH
        print("Trying manual deployment...")
        
        # Create a temporary script to deploy the key
        deploy_script = f"""
mkdir -p ~/.ssh
chmod 700 ~/.ssh
echo '{public_key}' >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
"""
        
        # Write script to temp file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False) as f:
            f.write(deploy_script)
            temp_script = f.name
        
        try:
            # Copy script to Pi and execute
            scp_cmd = f"scp {temp_script} {pi_user}@{pi_host}:~/deploy_key.sh"
            result = subprocess.run(scp_cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Script copied to Pi")
                
                # Execute the script
                ssh_cmd = f"ssh {pi_user}@{pi_host} 'chmod +x ~/deploy_key.sh && ~/deploy_key.sh && rm ~/deploy_key.sh'"
                result = subprocess.run(ssh_cmd, shell=True, capture_output=True, text=True)
                
                if result.returncode == 0:
                    print("✅ Public key deployed successfully")
                else:
                    print(f"❌ Script execution failed: {result.stderr}")
                    return False
            else:
                print(f"❌ Script copy failed: {result.stderr}")
                return False
                
        finally:
            # Clean up temp file
            try:
                os.unlink(temp_script)
            except:
                pass
    
    # Step 4: Test the connection
    print("\n🧪 Testing SSH connection...")
    
    test_cmd = f"ssh -i {key_path} -o PasswordAuthentication=no -o ConnectTimeout=10 {pi_user}@{pi_host} 'echo SSH_TEST_SUCCESS'"
    result = subprocess.run(test_cmd, shell=True, capture_output=True, text=True)
    
    if result.returncode == 0 and "SSH_TEST_SUCCESS" in result.stdout:
        print("✅ SSH key authentication working!")
        return True
    else:
        print(f"❌ SSH test failed: {result.stderr}")
        return False

if __name__ == '__main__':
    success = main()
    if success:
        print("\n🎉 SSH authentication setup complete!")
        print("You can now use the camera system without password prompts.")
    else:
        print("\n❌ SSH authentication setup failed.")
        print("You may need to check your Pi's SSH configuration.")
    
    input("\nPress Enter to continue...")
