#!/usr/bin/env python3
"""
Alternative file copy methods when SSH is not working
"""

import os
import shutil
import subprocess
import sys

def create_file_package():
    """Create a package of files that can be transferred"""
    print("📦 Creating file package for transfer...")
    
    # Files to include
    files_to_copy = [
        "kinect_unified_streamer.py",
        "apply_streaming_fix.py",
        "simple_fix.py",
        "fix_freenect_capture.py",
        "check_drivers.py",
        "restart_pi_service.py"
    ]
    
    # Create a directory for the package
    package_dir = "pi_fix_package"
    if os.path.exists(package_dir):
        shutil.rmtree(package_dir)
    os.makedirs(package_dir)
    
    # Copy files
    copied_files = []
    for file in files_to_copy:
        if os.path.exists(file):
            shutil.copy2(file, package_dir)
            copied_files.append(file)
            print(f"✅ Copied {file}")
        else:
            print(f"⚠️  {file} not found")
    
    # Create a README with instructions
    readme_content = """# Pi Fix Package

## Files included:
""" + "\n".join([f"- {f}" for f in copied_files]) + """

## Instructions:

1. Copy this entire folder to the Pi using one of these methods:
   - USB drive
   - Email attachment
   - Network share
   - Any other file transfer method

2. On the Pi, extract/copy the files to: /home/ls/kinect_ws/src/

3. Run the appropriate fix script:
   - For simple fix: python3 simple_fix.py
   - For advanced fix: python3 fix_freenect_capture.py
   - For driver check: python3 check_drivers.py

4. Restart the service: python3 restart_pi_service.py

## Troubleshooting:
- If freenect is not working, try the simple_fix.py first
- If you need to check drivers, run check_drivers.py
- The service should show frame capture progress when working
"""
    
    with open(os.path.join(package_dir, "README.txt"), "w") as f:
        f.write(readme_content)
    
    print(f"\n✅ Package created in '{package_dir}' folder")
    print(f"   Contains {len(copied_files)} files")
    print(f"   Copy this folder to the Pi using USB, email, or other method")
    
    return package_dir

def create_zip_package():
    """Create a ZIP file for easy transfer"""
    print("\n📦 Creating ZIP package...")
    
    try:
        import zipfile
        
        package_dir = create_file_package()
        zip_name = "pi_fix_package.zip"
        
        with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(package_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arc_path = os.path.relpath(file_path, package_dir)
                    zipf.write(file_path, arc_path)
        
        print(f"✅ ZIP package created: {zip_name}")
        print(f"   Size: {os.path.getsize(zip_name)} bytes")
        print(f"   Transfer this file to the Pi and extract it")
        
        return zip_name
        
    except ImportError:
        print("❌ ZIP module not available, using folder package only")
        return None

def create_manual_instructions():
    """Create manual instructions for file transfer"""
    print("\n📝 Creating manual transfer instructions...")
    
    instructions = """# Manual File Transfer Instructions

## Method 1: USB Drive
1. Copy the pi_fix_package folder to a USB drive
2. Connect USB drive to Pi
3. Mount and copy files:
   ```bash
   sudo mkdir -p /mnt/usb
   sudo mount /dev/sda1 /mnt/usb  # Adjust device as needed
   cp -r /mnt/usb/pi_fix_package/* /home/ls/kinect_ws/src/
   sudo umount /mnt/usb
   ```

## Method 2: Email
1. Email the pi_fix_package.zip file to yourself
2. On Pi, download and extract:
   ```bash
   # Download email attachment or use wget/curl
   unzip pi_fix_package.zip
   cp -r pi_fix_package/* /home/ls/kinect_ws/src/
   ```

## Method 3: Network Share
1. Share the pi_fix_package folder on Windows
2. On Pi, mount the share:
   ```bash
   sudo mkdir -p /mnt/windows
   sudo mount -t cifs //192.168.1.218/shared_folder /mnt/windows -o username=your_username
   cp -r /mnt/windows/pi_fix_package/* /home/ls/kinect_ws/src/
   ```

## Method 4: Direct Edit
If file transfer is impossible, manually edit the file on Pi:
1. SSH into Pi (if possible)
2. Edit: nano /home/ls/kinect_ws/src/kinect_unified_streamer.py
3. Find line 208 and change:
   ```python
   if self.kinect_method == 'freenect':
   ```
   To:
   ```python
   if self.kinect_method in ['freenect', 'freenect_system']:
   ```
4. Save and restart service

## After Transfer:
1. Make files executable: chmod +x *.py
2. Run fix: python3 simple_fix.py
3. Test: python3 quick_test.py 192.168.1.9
"""
    
    with open("MANUAL_TRANSFER_INSTRUCTIONS.txt", "w") as f:
        f.write(instructions)
    
    print("✅ Manual instructions created: MANUAL_TRANSFER_INSTRUCTIONS.txt")

def main():
    """Main function"""
    print("📦 ALTERNATIVE FILE TRANSFER TOOL")
    print("="*50)
    print("This tool creates packages for transferring files when SSH fails")
    print()
    
    # Create file package
    package_dir = create_file_package()
    
    # Create ZIP package
    zip_file = create_zip_package()
    
    # Create instructions
    create_manual_instructions()
    
    print("\n" + "="*50)
    print("PACKAGE CREATION COMPLETE")
    print("="*50)
    print("\n📋 FILES CREATED:")
    print(f"   📁 {package_dir}/ - Folder with all files")
    if zip_file:
        print(f"   📦 {zip_file} - ZIP archive")
    print("   📝 MANUAL_TRANSFER_INSTRUCTIONS.txt - Transfer guide")
    
    print("\n🚀 NEXT STEPS:")
    print("1. Choose a transfer method from the instructions")
    print("2. Copy the package to the Pi")
    print("3. Run the appropriate fix script on the Pi")
    print("4. Test the streaming service")

if __name__ == "__main__":
    main()
