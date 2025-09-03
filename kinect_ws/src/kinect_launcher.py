#!/usr/bin/env python3
"""
Simplified Kinect Launcher
Easy-to-use launcher for the unified Kinect streaming system
"""

import subprocess
import sys
import os
import time
import threading
import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser
import requests

class KinectLauncher:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Kinect Camera Launcher")
        self.root.geometry("600x500")
        self.root.resizable(False, False)
        
        # Configuration
        self.pi_ip = tk.StringVar(value="192.168.1.9")  # Default Pi IP
        self.pi_port = tk.StringVar(value="8080")
        self.pi_user = tk.StringVar(value="ls")  # Default Pi user
        self.streamer_process = None
        self.viewer_process = None
        
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the user interface"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="🎥 Kinect Camera Launcher", 
                               font=("Arial", 18, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Configuration frame
        config_frame = ttk.LabelFrame(main_frame, text="Configuration", padding="15")
        config_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Pi IP configuration
        ip_frame = ttk.Frame(config_frame)
        ip_frame.pack(fill=tk.X, pady=5)
        ttk.Label(ip_frame, text="Raspberry Pi IP:").pack(side=tk.LEFT)
        ip_entry = ttk.Entry(ip_frame, textvariable=self.pi_ip, width=20)
        ip_entry.pack(side=tk.RIGHT)
        
        # Pi User configuration
        user_frame = ttk.Frame(config_frame)
        user_frame.pack(fill=tk.X, pady=5)
        ttk.Label(user_frame, text="Pi Username:").pack(side=tk.LEFT)
        user_entry = ttk.Entry(user_frame, textvariable=self.pi_user, width=15)
        user_entry.pack(side=tk.RIGHT)
        
        # Port configuration
        port_frame = ttk.Frame(config_frame)
        port_frame.pack(fill=tk.X, pady=5)
        ttk.Label(port_frame, text="Port:").pack(side=tk.LEFT)
        port_entry = ttk.Entry(port_frame, textvariable=self.pi_port, width=10)
        port_entry.pack(side=tk.RIGHT)
        
        # Control buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Main launch button
        self.launch_btn = ttk.Button(button_frame, text="🚀 Start Kinect Stream", 
                                   command=self.start_kinect_stream, style="Accent.TButton")
        self.launch_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Stop button
        self.stop_btn = ttk.Button(button_frame, text="⏹️ Stop Stream", 
                                 command=self.stop_kinect_stream, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Test connection button
        self.test_btn = ttk.Button(button_frame, text="🔍 Test Connection", 
                                 command=self.test_connection)
        self.test_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Open browser button
        self.browser_btn = ttk.Button(button_frame, text="🌐 Open in Browser", 
                                    command=self.open_browser)
        self.browser_btn.pack(side=tk.LEFT)
        
        # Status frame
        status_frame = ttk.LabelFrame(main_frame, text="Status", padding="10")
        status_frame.pack(fill=tk.BOTH, expand=True)
        
        # Status text
        self.status_text = tk.Text(status_frame, height=12, width=60, wrap=tk.WORD)
        self.status_text.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar for status text
        scrollbar = ttk.Scrollbar(status_frame, orient=tk.VERTICAL, command=self.status_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.status_text.configure(yscrollcommand=scrollbar.set)
        
        # Quick access frame
        quick_frame = ttk.LabelFrame(main_frame, text="Quick Access", padding="10")
        quick_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Quick access buttons
        quick_btn_frame = ttk.Frame(quick_frame)
        quick_btn_frame.pack(fill=tk.X)
        
        ttk.Button(quick_btn_frame, text="📱 Open PC Viewer", 
                  command=self.open_pc_viewer).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(quick_btn_frame, text="📁 Sync Files to Pi", 
                  command=self.sync_files).pack(side=tk.LEFT, padx=5)
        
    def log_message(self, message):
        """Log a message to the status text area"""
        timestamp = time.strftime("%H:%M:%S")
        self.status_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.status_text.see(tk.END)
        self.root.update_idletasks()
        
    def test_connection(self):
        """Test connection to Raspberry Pi"""
        self.log_message("🔍 Testing connection to Raspberry Pi...")
        
        def test_connection():
            try:
                url = f"http://{self.pi_ip.get()}:{self.pi_port.get()}/status"
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    status = response.json()
                    self.root.after(0, lambda: self.log_message("✅ Pi connection successful!"))
                    self.root.after(0, lambda: self.log_message(f"   Kinect available: {status.get('kinect_available', 'Unknown')}"))
                    self.root.after(0, lambda: self.log_message(f"   Method: {status.get('kinect_method', 'Unknown')}"))
                    self.root.after(0, lambda: self.log_message(f"   Frames: {status.get('frame_count', 0)}"))
                else:
                    self.root.after(0, lambda: self.log_message(f"❌ Pi connection failed: HTTP {response.status_code}"))
            except Exception as e:
                error_msg = str(e)
                self.root.after(0, lambda: self.log_message(f"❌ Pi connection failed: {error_msg}"))
        
        # Run test in separate thread
        threading.Thread(target=test_connection, daemon=True).start()
    
    def start_kinect_stream(self):
        """Start the Kinect streaming on Pi"""
        self.log_message("🚀 Starting Kinect stream on Raspberry Pi...")
        
        # Disable launch button and enable stop button
        self.launch_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        
        def start_stream():
            try:
                # Check if stream is already running
                url = f"http://{self.pi_ip.get()}:{self.pi_port.get()}/status"
                response = requests.get(url, timeout=3)
                if response.status_code == 200:
                    self.root.after(0, lambda: self.log_message("✅ Kinect stream already running"))
                    return
            except:
                pass
            
            # Try to start the stream on Pi using SSH
            try:
                # Use the unified streamer
                cmd = f"ssh {self.pi_user.get()}@{self.pi_ip.get()} 'cd ~/kinect_ws && python3 kinect_unified_streamer.py --host 0.0.0.0 --port {self.pi_port.get()} &'"
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                
                if result.returncode == 0:
                    self.root.after(0, lambda: self.log_message("✅ Started Kinect stream on Pi"))
                    # Wait a moment and test connection
                    time.sleep(3)
                    self.root.after(0, self.test_connection)
                else:
                    self.root.after(0, lambda: self.log_message(f"❌ Failed to start stream: {result.stderr}"))
                    self.root.after(0, lambda: self.log_message("   Make sure SSH is working and files are synced"))
                    
            except Exception as e:
                error_msg = str(e)
                self.root.after(0, lambda: self.log_message(f"❌ Error starting stream: {error_msg}"))
        
        threading.Thread(target=start_stream, daemon=True).start()
        
    def stop_kinect_stream(self):
        """Stop the Kinect streaming"""
        self.log_message("⏹️ Stopping Kinect stream...")
        
        try:
            # Try to stop the stream on Pi
            cmd = f"ssh {self.pi_user.get()}@{self.pi_ip.get()} 'pkill -f kinect_unified_streamer'"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.log_message("✅ Kinect stream stopped")
            else:
                self.log_message("⚠️ Could not stop stream (may not be running)")
                
        except Exception as e:
            self.log_message(f"⚠️ Error stopping stream: {e}")
        
        # Re-enable launch button and disable stop button
        self.launch_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        
    def open_browser(self):
        """Open Kinect stream in browser"""
        url = f"http://{self.pi_ip.get()}:{self.pi_port.get()}"
        self.log_message(f"🌐 Opening Kinect stream in browser: {url}")
        try:
            webbrowser.open(url)
        except Exception as e:
            self.log_message(f"❌ Could not open browser: {e}")
            
    def open_pc_viewer(self):
        """Open the PC camera viewer"""
        self.log_message("🖥️ Opening PC camera viewer...")
        
        try:
            # Get the directory of this script
            script_dir = os.path.dirname(os.path.abspath(__file__))
            viewer_script = os.path.join(script_dir, "windows_camera_viewer.py")
            
            if not os.path.exists(viewer_script):
                self.log_message("❌ PC viewer script not found!")
                return
            
            # Start the viewer process
            self.viewer_process = subprocess.Popen([
                sys.executable, viewer_script
            ], cwd=script_dir)
            
            self.log_message("✅ PC camera viewer started")
            
        except Exception as e:
            self.log_message(f"❌ Failed to start PC viewer: {e}")
    
    def sync_files(self):
        """Sync files to Raspberry Pi"""
        self.log_message("📁 Syncing files to Raspberry Pi...")
        
        def sync_files():
            try:
                # Use the quick sync batch file
                script_dir = os.path.dirname(os.path.abspath(__file__))
                sync_script = os.path.join(script_dir, "quick_sync.bat")
                
                if os.path.exists(sync_script):
                    result = subprocess.run([sync_script], cwd=script_dir, 
                                          capture_output=True, text=True)
                    if result.returncode == 0:
                        self.root.after(0, lambda: self.log_message("✅ Files synced successfully"))
                    else:
                        self.root.after(0, lambda: self.log_message(f"❌ Sync failed: {result.stderr}"))
                else:
                    # Manual sync
                    files_to_sync = [
                        "kinect_unified_streamer.py",
                        "windows_camera_viewer.py",
                        "requirements.txt"
                    ]
                    
                    for file in files_to_sync:
                        if os.path.exists(file):
                            cmd = f"scp {file} {self.pi_user.get()}@{self.pi_ip.get()}:~/kinect_ws/"
                            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                            if result.returncode == 0:
                                self.root.after(0, lambda f=file: self.log_message(f"✅ Synced {f}"))
                            else:
                                self.root.after(0, lambda f=file: self.log_message(f"❌ Failed to sync {f}"))
                    
            except Exception as e:
                error_msg = str(e)
                self.root.after(0, lambda: self.log_message(f"❌ Sync error: {error_msg}"))
        
        threading.Thread(target=sync_files, daemon=True).start()
        
    def on_closing(self):
        """Handle window closing"""
        if self.viewer_process:
            try:
                self.viewer_process.terminate()
            except:
                pass
        self.root.destroy()
        
    def run(self):
        """Run the launcher application"""
        self.log_message("🎯 Kinect Camera Launcher ready!")
        self.log_message("Configure your Pi IP address and click 'Start Kinect Stream'")
        self.log_message("")
        self.log_message("📋 Quick Start:")
        self.log_message("1. Make sure your Pi IP is correct")
        self.log_message("2. Click 'Sync Files to Pi' to upload the latest code")
        self.log_message("3. Click 'Start Kinect Stream' to begin streaming")
        self.log_message("4. Click 'Open in Browser' to view the stream")
        self.log_message("5. Use 'Open PC Viewer' for a dedicated viewer app")
        
        # Handle window closing
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Start the application
        self.root.mainloop()

def main():
    """Main function"""
    print("Starting Kinect Camera Launcher...")
    
    # Check if required modules are available
    try:
        import requests
        import tkinter
    except ImportError as e:
        print(f"Error: Required module not available: {e}")
        print("Please install required packages:")
        print("pip install requests")
        input("Press Enter to exit...")
        return 1
    
    # Create and run the launcher
    launcher = KinectLauncher()
    launcher.run()
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
