#!/usr/bin/env python3
"""
Comprehensive Kinect Diagnostic Tool
Identifies issues preventing Kinect camera feed from working
"""

import sys
import os
import subprocess
import time
import requests
import json
from pathlib import Path

class KinectDiagnostic:
    def __init__(self):
        self.issues = []
        self.recommendations = []
        self.pi_ip = "192.168.1.9"  # Default Pi IP
        self.pi_port = "8080"
        
    def log_issue(self, issue, severity="WARNING"):
        """Log an issue found during diagnosis"""
        self.issues.append(f"[{severity}] {issue}")
        print(f"❌ {severity}: {issue}")
    
    def log_recommendation(self, recommendation):
        """Log a recommendation to fix issues"""
        self.recommendations.append(recommendation)
        print(f"💡 RECOMMENDATION: {recommendation}")
    
    def log_success(self, message):
        """Log a successful check"""
        print(f"✅ {message}")
    
    def check_python_environment(self):
        """Check Python environment and dependencies"""
        print("\n🔍 Checking Python Environment...")
        
        # Check Python version
        python_version = sys.version_info
        if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 7):
            self.log_issue(f"Python version {python_version.major}.{python_version.minor} is too old. Need Python 3.7+")
        else:
            self.log_success(f"Python version {python_version.major}.{python_version.minor} is compatible")
        
        # Check required modules
        required_modules = [
            ('cv2', 'opencv-python'),
            ('numpy', 'numpy'),
            ('PIL', 'pillow'),
            ('requests', 'requests'),
            ('tkinter', 'tkinter (usually included with Python)')
        ]
        
        for module, package in required_modules:
            try:
                __import__(module)
                self.log_success(f"Module '{module}' is available")
            except ImportError:
                self.log_issue(f"Module '{module}' not found. Install with: pip install {package}")
    
    def check_kinect_libraries(self):
        """Check for Kinect-specific libraries"""
        print("\n🔍 Checking Kinect Libraries...")
        
        # Check freenect Python library
        try:
            import freenect
            self.log_success("freenect Python library is available")
        except ImportError:
            self.log_issue("freenect Python library not found")
            self.log_recommendation("Install freenect: pip install freenect")
            self.log_recommendation("Or on Pi: sudo apt-get install python3-freenect")
        
        # Check for libfreenect system library
        try:
            import ctypes
            freenect_lib = ctypes.cdll.LoadLibrary('/usr/local/lib/libfreenect.so')
            self.log_success("libfreenect system library found")
        except OSError:
            self.log_issue("libfreenect system library not found")
            self.log_recommendation("Install libfreenect: sudo apt-get install libfreenect-dev")
    
    def check_camera_devices(self):
        """Check for available camera devices"""
        print("\n🔍 Checking Camera Devices...")
        
        try:
            import cv2
            
            # Check for video devices
            video_devices = []
            for i in range(10):  # Check first 10 devices
                cap = cv2.VideoCapture(i)
                if cap.isOpened():
                    ret, frame = cap.read()
                    if ret and frame is not None:
                        video_devices.append(i)
                        self.log_success(f"Camera device {i} is working")
                    else:
                        self.log_issue(f"Camera device {i} opened but cannot read frames")
                cap.release()
            
            if not video_devices:
                self.log_issue("No working camera devices found")
                self.log_recommendation("Check camera connections and permissions")
                self.log_recommendation("Try: ls -la /dev/video*")
            else:
                self.log_success(f"Found {len(video_devices)} working camera device(s): {video_devices}")
                
        except Exception as e:
            self.log_issue(f"Error checking camera devices: {e}")
    
    def check_network_connectivity(self):
        """Check network connectivity to Raspberry Pi"""
        print("\n🔍 Checking Network Connectivity...")
        
        # Test ping to Pi
        try:
            result = subprocess.run(['ping', '-c', '1', self.pi_ip], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                self.log_success(f"Ping to {self.pi_ip} successful")
            else:
                self.log_issue(f"Ping to {self.pi_ip} failed")
                self.log_recommendation("Check Pi IP address and network connection")
        except Exception as e:
            self.log_issue(f"Ping test failed: {e}")
        
        # Test SSH connection
        try:
            result = subprocess.run(['ssh', '-o', 'ConnectTimeout=5', 
                                   f'ls@{self.pi_ip}', 'echo test'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0 and 'test' in result.stdout:
                self.log_success("SSH connection to Pi successful")
            else:
                self.log_issue("SSH connection to Pi failed")
                self.log_recommendation("Check SSH configuration and Pi username")
        except Exception as e:
            self.log_issue(f"SSH test failed: {e}")
    
    def check_pi_streaming_service(self):
        """Check if streaming service is running on Pi"""
        print("\n🔍 Checking Pi Streaming Service...")
        
        try:
            url = f"http://{self.pi_ip}:{self.pi_port}/status"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                status = response.json()
                self.log_success("Streaming service is running on Pi")
                self.log_success(f"Kinect available: {status.get('kinect_available', 'Unknown')}")
                self.log_success(f"Method: {status.get('kinect_method', 'Unknown')}")
                self.log_success(f"Frames: {status.get('frame_count', 0)}")
                
                if not status.get('kinect_available', False):
                    self.log_issue("Kinect is not available on Pi")
                    self.log_recommendation("Check Kinect hardware connection on Pi")
                    self.log_recommendation("Run: python3 kinect_unified_streamer.py on Pi")
            else:
                self.log_issue(f"Streaming service returned status code: {response.status_code}")
                self.log_recommendation("Start streaming service on Pi")
                
        except requests.exceptions.ConnectionError:
            self.log_issue("Cannot connect to streaming service on Pi")
            self.log_recommendation("Start streaming service: python3 kinect_unified_streamer.py")
        except Exception as e:
            self.log_issue(f"Error checking streaming service: {e}")
    
    def check_file_sync(self):
        """Check if files are properly synced to Pi"""
        print("\n🔍 Checking File Sync...")
        
        required_files = [
            'kinect_unified_streamer.py',
            'windows_camera_viewer.py',
            'requirements.txt'
        ]
        
        try:
            for file in required_files:
                cmd = f"ssh ls@{self.pi_ip} 'test -f ~/kinect_ws/{file} && echo exists'"
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                
                if 'exists' in result.stdout:
                    self.log_success(f"File {file} exists on Pi")
                else:
                    self.log_issue(f"File {file} not found on Pi")
                    self.log_recommendation(f"Sync file: scp {file} ls@{self.pi_ip}:~/kinect_ws/")
                    
        except Exception as e:
            self.log_issue(f"Error checking file sync: {e}")
    
    def check_pi_dependencies(self):
        """Check if Pi has required dependencies"""
        print("\n🔍 Checking Pi Dependencies...")
        
        try:
            # Check Python packages
            cmd = f"ssh ls@{self.pi_ip} 'python3 -c \"import cv2, numpy, PIL, requests; print(\\\"All packages available\\\")\"'"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if 'All packages available' in result.stdout:
                self.log_success("All required Python packages are installed on Pi")
            else:
                self.log_issue("Missing Python packages on Pi")
                self.log_recommendation("Install packages: pip3 install -r ~/kinect_ws/requirements.txt")
                
        except Exception as e:
            self.log_issue(f"Error checking Pi dependencies: {e}")
    
    def generate_report(self):
        """Generate a comprehensive diagnostic report"""
        print("\n" + "="*60)
        print("🎯 KINECT DIAGNOSTIC REPORT")
        print("="*60)
        
        if not self.issues:
            print("🎉 No issues found! Your Kinect system should be working.")
        else:
            print(f"❌ Found {len(self.issues)} issue(s):")
            for i, issue in enumerate(self.issues, 1):
                print(f"   {i}. {issue}")
        
        if self.recommendations:
            print(f"\n💡 Recommendations ({len(self.recommendations)}):")
            for i, rec in enumerate(self.recommendations, 1):
                print(f"   {i}. {rec}")
        
        print("\n📋 Quick Fix Commands:")
        print("   1. Sync files: quick_sync.bat")
        print("   2. Start launcher: start_kinect_system.bat")
        print("   3. Manual Pi start: ssh ls@192.168.1.9 'cd ~/kinect_ws && python3 kinect_unified_streamer.py'")
        
        print("\n🌐 Access URLs:")
        print(f"   - Pi Stream: http://{self.pi_ip}:{self.pi_port}")
        print(f"   - Status: http://{self.pi_ip}:{self.pi_port}/status")
        print(f"   - Diagnostic: http://{self.pi_ip}:{self.pi_port}/diagnostic")
    
    def run_full_diagnostic(self):
        """Run complete diagnostic check"""
        print("🔍 Starting Comprehensive Kinect Diagnostic...")
        print("This will check all components of your Kinect streaming system.\n")
        
        self.check_python_environment()
        self.check_kinect_libraries()
        self.check_camera_devices()
        self.check_network_connectivity()
        self.check_file_sync()
        self.check_pi_dependencies()
        self.check_pi_streaming_service()
        
        self.generate_report()

def main():
    """Main function"""
    diagnostic = KinectDiagnostic()
    diagnostic.run_full_diagnostic()
    
    print("\nPress Enter to exit...")
    input()

if __name__ == '__main__':
    main()
