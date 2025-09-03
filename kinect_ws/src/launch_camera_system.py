#!/usr/bin/env python3
"""
Comprehensive camera system launcher
Handles Pi connectivity, streaming service, and camera viewer
"""

import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import threading
import time
import requests
import os
import sys

class CameraSystemLauncher:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Camera System Launcher")
        self.root.geometry("600x500")
        
        # Configuration
        self.pi_host = "192.168.1.9"
        self.pi_port = 8080
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the user interface"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="🎥 Camera System Launcher", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Status frame
        status_frame = ttk.LabelFrame(main_frame, text="System Status", padding="10")
        status_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.status_label = ttk.Label(status_frame, text="Status: Checking...", 
                                    foreground="orange")
        self.status_label.grid(row=0, column=0, sticky=tk.W)
        
        # Pi configuration
        config_frame = ttk.LabelFrame(main_frame, text="Pi Configuration", padding="10")
        config_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(config_frame, text="Pi IP Address:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.pi_ip_entry = ttk.Entry(config_frame, width=20)
        self.pi_ip_entry.insert(0, self.pi_host)
        self.pi_ip_entry.grid(row=0, column=1, padx=(5, 0), pady=5)
        
        ttk.Label(config_frame, text="Port:").grid(row=0, column=2, sticky=tk.W, padx=(10, 0), pady=5)
        self.pi_port_entry = ttk.Entry(config_frame, width=10)
        self.pi_port_entry.insert(0, str(self.pi_port))
        self.pi_port_entry.grid(row=0, column=3, padx=(5, 0), pady=5)
        
        # Control buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=10)
        
        self.check_button = ttk.Button(button_frame, text="🔍 Check Pi Status", 
                                     command=self.check_pi_status)
        self.check_button.grid(row=0, column=0, padx=5)
        
        self.start_pi_button = ttk.Button(button_frame, text="🚀 Start Pi Streaming", 
                                        command=self.start_pi_streaming)
        self.start_pi_button.grid(row=0, column=1, padx=5)
        
        self.viewer_button = ttk.Button(button_frame, text="📺 Open Camera Viewer", 
                                      command=self.open_camera_viewer, state="disabled")
        self.viewer_button.grid(row=0, column=2, padx=5)
        
        # Log frame
        log_frame = ttk.LabelFrame(main_frame, text="System Log", padding="10")
        log_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        self.log_text = tk.Text(log_frame, height=12, width=70)
        scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(4, weight=1)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        # Start initial check
        self.root.after(1000, self.check_pi_status)
    
    def log(self, message):
        """Add message to log"""
        timestamp = time.strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"
        self.log_text.insert(tk.END, log_message)
        self.log_text.see(tk.END)
        self.root.update_idletasks()
        print(log_message.strip())
    
    def check_pi_status(self):
        """Check Pi connectivity and streaming service"""
        self.log("🔍 Checking Pi status...")
        self.status_label.config(text="Status: Checking...", foreground="orange")
        
        def check_thread():
            try:
                # Update configuration
                self.pi_host = self.pi_ip_entry.get()
                self.pi_port = int(self.pi_port_entry.get())
                
                # Check connectivity
                self.log(f"📡 Pinging {self.pi_host}...")
                result = subprocess.run(['ping', '-n', '1', self.pi_host], 
                                      capture_output=True, text=True, timeout=5)
                
                if result.returncode != 0:
                    self.root.after(0, lambda: self.log("❌ Pi is not reachable"))
                    self.root.after(0, lambda: self.status_label.config(
                        text="Status: Pi Offline", foreground="red"))
                    return
                
                self.log("✅ Pi is reachable")
                
                # Check streaming service
                self.log(f"🌐 Checking streaming service at {self.pi_host}:{self.pi_port}...")
                try:
                    response = requests.get(f'http://{self.pi_host}:{self.pi_port}/status', timeout=5)
                    if response.status_code == 200:
                        self.log("✅ Streaming service is running")
                        self.root.after(0, lambda: self.status_label.config(
                            text="Status: Ready", foreground="green"))
                        self.root.after(0, lambda: self.viewer_button.config(state="normal"))
                    else:
                        self.log(f"⚠️ Streaming service returned status {response.status_code}")
                        self.root.after(0, lambda: self.status_label.config(
                            text="Status: Pi Online, Service Down", foreground="orange"))
                except requests.exceptions.RequestException as e:
                    self.log(f"❌ Streaming service not responding: {e}")
                    self.root.after(0, lambda: self.status_label.config(
                        text="Status: Pi Online, Service Down", foreground="orange"))
                
            except Exception as e:
                self.log(f"❌ Error checking Pi status: {e}")
                self.root.after(0, lambda: self.status_label.config(
                    text="Status: Error", foreground="red"))
        
        threading.Thread(target=check_thread, daemon=True).start()
    
    def start_pi_streaming(self):
        """Start Pi streaming service"""
        self.log("🚀 Starting Pi streaming service...")
        
        def start_thread():
            try:
                # Run the start streaming script
                script_path = os.path.join(os.path.dirname(__file__), 'start_pi_streaming.py')
                if os.path.exists(script_path):
                    result = subprocess.run([sys.executable, script_path], 
                                          capture_output=True, text=True, input="\n".join([
                                              self.pi_host, "ls", "pointsperspectivedanglecrouches"
                                          ]))
                    
                    if result.returncode == 0:
                        self.log("✅ Pi streaming service started")
                        self.root.after(0, lambda: self.check_pi_status())
                    else:
                        self.log(f"❌ Failed to start streaming service: {result.stderr}")
                else:
                    self.log("❌ start_pi_streaming.py not found")
                    
            except Exception as e:
                self.log(f"❌ Error starting streaming service: {e}")
        
        threading.Thread(target=start_thread, daemon=True).start()
    
    def open_camera_viewer(self):
        """Open the camera viewer"""
        self.log("📺 Opening camera viewer...")
        
        try:
            # Update configuration
            self.pi_host = self.pi_ip_entry.get()
            self.pi_port = int(self.pi_port_entry.get())
            
            # Get the script directory
            script_dir = os.path.dirname(os.path.abspath(__file__))
            viewer_file = os.path.join(script_dir, 'windows_camera_viewer_fixed.py')
            
            if not os.path.exists(viewer_file):
                self.log("❌ Camera viewer file not found")
                messagebox.showerror("Error", "Camera viewer file not found!")
                return
            
            # Try different Python commands
            python_commands = ['python', 'python3', 'py']
            
            for python_cmd in python_commands:
                try:
                    viewer_cmd = [python_cmd, viewer_file]
                    subprocess.Popen(viewer_cmd, shell=True)
                    self.log(f"✅ Camera viewer opened using {python_cmd}")
                    return
                except FileNotFoundError:
                    continue
            
            # If all Python commands fail, try opening with default program
            self.log("⚠️ Python command not found, trying default program...")
            os.startfile(viewer_file)
            self.log("✅ Camera viewer opened with default program")
            
        except Exception as e:
            self.log(f"❌ Failed to open camera viewer: {e}")
            messagebox.showerror("Error", f"Failed to open camera viewer:\n{e}")
    
    def run(self):
        """Run the launcher"""
        self.log("🚀 Camera System Launcher started")
        self.root.mainloop()

if __name__ == '__main__':
    launcher = CameraSystemLauncher()
    launcher.run()