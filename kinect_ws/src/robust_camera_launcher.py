#!/usr/bin/env python3
"""
Robust Camera System Launcher
Handles network connectivity issues and automatically retries connections
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import subprocess
import threading
import time
import requests
import json
import os
import sys

class RobustCameraLauncher:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Robust Camera System Launcher")
        self.root.geometry("800x600")
        
        # Configuration
        self.pi_host = "192.168.1.9"
        self.pi_user = "ls"
        self.ssh_key = r"C:\Users\lysan\.ssh\pi_kinect_ls_192_168_1_9_key"
        self.camera_port = 8080
        
        # State
        self.pi_online = False
        self.camera_running = False
        self.retry_count = 0
        self.max_retries = 5
        
        self.setup_ui()
        self.start_network_monitor()
    
    def setup_ui(self):
        """Setup the user interface"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="Robust Camera System Launcher", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Status frame
        status_frame = ttk.LabelFrame(main_frame, text="System Status", padding="10")
        status_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Pi status
        self.pi_status_label = ttk.Label(status_frame, text="Pi Status: Checking...", 
                                        foreground="orange")
        self.pi_status_label.grid(row=0, column=0, sticky=tk.W)
        
        # Camera status
        self.camera_status_label = ttk.Label(status_frame, text="Camera Status: Unknown", 
                                            foreground="orange")
        self.camera_status_label.grid(row=1, column=0, sticky=tk.W)
        
        # Network status
        self.network_status_label = ttk.Label(status_frame, text="Network: Checking...", 
                                             foreground="orange")
        self.network_status_label.grid(row=2, column=0, sticky=tk.W)
        
        # Control frame
        control_frame = ttk.LabelFrame(main_frame, text="Controls", padding="10")
        control_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Buttons
        self.start_button = ttk.Button(control_frame, text="Start Camera System", 
                                      command=self.start_camera_system)
        self.start_button.grid(row=0, column=0, padx=(0, 10))
        
        self.stop_button = ttk.Button(control_frame, text="Stop Camera System", 
                                     command=self.stop_camera_system, state="disabled")
        self.stop_button.grid(row=0, column=1, padx=(0, 10))
        
        self.viewer_button = ttk.Button(control_frame, text="Open Camera Viewer", 
                                       command=self.open_camera_viewer, state="disabled")
        self.viewer_button.grid(row=0, column=2, padx=(0, 10))
        
        self.retry_button = ttk.Button(control_frame, text="Retry Connection", 
                                      command=self.retry_connection)
        self.retry_button.grid(row=0, column=3)
        
        # Configuration frame
        config_frame = ttk.LabelFrame(main_frame, text="Configuration", padding="10")
        config_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Pi IP
        ttk.Label(config_frame, text="Pi IP Address:").grid(row=0, column=0, sticky=tk.W)
        self.pi_ip_entry = ttk.Entry(config_frame, width=15)
        self.pi_ip_entry.insert(0, self.pi_host)
        self.pi_ip_entry.grid(row=0, column=1, padx=(5, 20))
        
        # Pi Username
        ttk.Label(config_frame, text="Pi Username:").grid(row=0, column=2, sticky=tk.W)
        self.pi_user_entry = ttk.Entry(config_frame, width=10)
        self.pi_user_entry.insert(0, self.pi_user)
        self.pi_user_entry.grid(row=0, column=3, padx=(5, 0))
        
        # Log frame
        log_frame = ttk.LabelFrame(main_frame, text="System Log", padding="10")
        log_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, width=80)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(4, weight=1)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
    
    def log(self, message):
        """Add message to log"""
        timestamp = time.strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"
        self.log_text.insert(tk.END, log_message)
        self.log_text.see(tk.END)
        self.root.update_idletasks()
        print(log_message.strip())
    
    def update_status(self, pi_status=None, camera_status=None, network_status=None):
        """Update status labels"""
        if pi_status:
            self.pi_status_label.config(text=f"Pi Status: {pi_status}")
        if camera_status:
            self.camera_status_label.config(text=f"Camera Status: {camera_status}")
        if network_status:
            self.network_status_label.config(text=f"Network: {network_status}")
    
    def check_pi_connectivity(self):
        """Check if Pi is reachable"""
        try:
            # Try ping
            result = subprocess.run(['ping', '-n', '1', self.pi_host], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                return True
        except:
            pass
        
        try:
            # Try SSH port
            result = subprocess.run(['Test-NetConnection', '-ComputerName', self.pi_host, '-Port', '22'], 
                                  capture_output=True, text=True, timeout=5)
            if 'TcpTestSucceeded : True' in result.stdout:
                return True
        except:
            pass
        
        return False
    
    def check_camera_status(self):
        """Check if camera stream is running"""
        try:
            response = requests.get(f'http://{self.pi_host}:{self.camera_port}/status', timeout=5)
            if response.status_code == 200:
                status = response.json()
                return status.get('running', False)
        except:
            pass
        return False
    
    def start_network_monitor(self):
        """Start background network monitoring"""
        def monitor():
            while True:
                try:
                    # Check Pi connectivity
                    pi_online = self.check_pi_connectivity()
                    if pi_online != self.pi_online:
                        self.pi_online = pi_online
                        if pi_online:
                            self.root.after(0, lambda: self.log("✅ Pi is online"))
                            self.root.after(0, lambda: self.update_status(pi_status="Online", network_status="Connected"))
                        else:
                            self.root.after(0, lambda: self.log("❌ Pi is offline"))
                            self.root.after(0, lambda: self.update_status(pi_status="Offline", network_status="Disconnected"))
                    
                    # Check camera status
                    if pi_online:
                        camera_running = self.check_camera_status()
                        if camera_running != self.camera_running:
                            self.camera_running = camera_running
                            if camera_running:
                                self.root.after(0, lambda: self.log("✅ Camera stream is running"))
                                self.root.after(0, lambda: self.update_status(camera_status="Running"))
                                self.root.after(0, lambda: self.viewer_button.config(state="normal"))
                            else:
                                self.root.after(0, lambda: self.log("❌ Camera stream is not running"))
                                self.root.after(0, lambda: self.update_status(camera_status="Stopped"))
                                self.root.after(0, lambda: self.viewer_button.config(state="disabled"))
                    
                    time.sleep(5)  # Check every 5 seconds
                    
                except Exception as e:
                    self.root.after(0, lambda: self.log(f"❌ Monitor error: {e}"))
                    time.sleep(10)
        
        monitor_thread = threading.Thread(target=monitor, daemon=True)
        monitor_thread.start()
    
    def start_camera_system(self):
        """Start the camera system on Pi"""
        self.log("🚀 Starting camera system...")
        self.start_button.config(state="disabled")
        
        def start_thread():
            try:
                # Update configuration
                self.pi_host = self.pi_ip_entry.get()
                self.pi_user = self.pi_user_entry.get()
                
                # Check if Pi is online
                if not self.check_pi_connectivity():
                    self.log("❌ Pi is not reachable. Please check network connection.")
                    self.start_button.config(state="normal")
                    return
                
                # Deploy files
                self.log("📁 Deploying camera files...")
                script_dir = os.path.dirname(os.path.abspath(__file__))
                
                # Files to deploy
                files_to_deploy = [
                    'kinect_unified_streamer.py',
                    'kinect_launcher.py',
                    'windows_camera_viewer.py',
                    'requirements.txt'
                ]
                
                for file in files_to_deploy:
                    file_path = os.path.join(script_dir, file)
                    if os.path.exists(file_path):
                        deploy_cmd = [
                            'scp', '-i', self.ssh_key, 
                            file_path, 
                            f'{self.pi_user}@{self.pi_host}:~/kinect_ws/'
                        ]
                        result = subprocess.run(deploy_cmd, capture_output=True, text=True)
                        if result.returncode != 0:
                            self.log(f"❌ Failed to deploy {file}: {result.stderr}")
                        else:
                            self.log(f"✅ Deployed {file}")
                    else:
                        self.log(f"⚠️ File not found: {file}")
                
                # Make scripts executable
                chmod_cmd = [
                    'ssh', '-i', self.ssh_key,
                    f'{self.pi_user}@{self.pi_host}',
                    'chmod +x ~/kinect_ws/*.py'
                ]
                subprocess.run(chmod_cmd, capture_output=True, text=True)
                
                # Start camera stream
                self.log("📹 Starting camera stream...")
                start_cmd = [
                    'ssh', '-i', self.ssh_key, 
                    '-o', 'ConnectTimeout=10', 
                    '-o', 'StrictHostKeyChecking=no',
                    f'{self.pi_user}@{self.pi_host}',
                    'cd ~/kinect_ws && python3 kinect_unified_streamer.py'
                ]
                
                # Start in background
                process = subprocess.Popen(start_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                self.log("✅ Camera system started")
                self.stop_button.config(state="normal")
                
            except Exception as e:
                self.log(f"❌ Failed to start camera system: {e}")
                self.start_button.config(state="normal")
        
        start_thread = threading.Thread(target=start_thread, daemon=True)
        start_thread.start()
    
    def stop_camera_system(self):
        """Stop the camera system"""
        self.log("🛑 Stopping camera system...")
        
        def stop_thread():
            try:
                stop_cmd = [
                    'ssh', '-i', self.ssh_key, 
                    '-o', 'ConnectTimeout=10', 
                    '-o', 'StrictHostKeyChecking=no',
                    f'{self.pi_user}@{self.pi_host}',
                    'pkill -f kinect_unified_streamer'
                ]
                subprocess.run(stop_cmd, capture_output=True, text=True)
                self.log("✅ Camera system stopped")
                self.stop_button.config(state="disabled")
                self.viewer_button.config(state="disabled")
                
            except Exception as e:
                self.log(f"❌ Failed to stop camera system: {e}")
        
        stop_thread = threading.Thread(target=stop_thread, daemon=True)
        stop_thread.start()
    
    def open_camera_viewer(self):
        """Open the camera viewer"""
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            viewer_file = os.path.join(script_dir, 'windows_camera_viewer.py')
            viewer_cmd = ['python', viewer_file]
            subprocess.Popen(viewer_cmd)
            self.log("✅ Camera viewer opened")
        except Exception as e:
            self.log(f"❌ Failed to open camera viewer: {e}")
    
    def retry_connection(self):
        """Retry connection to Pi"""
        self.log("🔄 Retrying connection...")
        self.retry_count += 1
        
        if self.retry_count > self.max_retries:
            self.log(f"❌ Max retries ({self.max_retries}) exceeded")
            return
        
        def retry_thread():
            for i in range(3):
                if self.check_pi_connectivity():
                    self.log("✅ Connection restored")
                    self.retry_count = 0
                    return
                time.sleep(2)
            
            self.log(f"❌ Retry {self.retry_count} failed")
        
        retry_thread = threading.Thread(target=retry_thread, daemon=True)
        retry_thread.start()
    
    def run(self):
        """Run the launcher"""
        self.log("🚀 Robust Camera System Launcher started")
        self.log(f"📡 Monitoring Pi at {self.pi_host}")
        self.root.mainloop()

if __name__ == '__main__':
    launcher = RobustCameraLauncher()
    launcher.run()
