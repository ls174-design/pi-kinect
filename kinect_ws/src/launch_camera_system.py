#!/usr/bin/env python3
"""
Camera System Launcher
Starts both the PC camera viewer and Pi camera stream with one click
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
from ssh_manager import SSHManager

class CameraSystemLauncher:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Camera System Launcher")
        self.root.geometry("500x400")
        self.root.resizable(False, False)
        
        # Configuration
        self.pi_ip = tk.StringVar(value="192.168.1.9")  # Default Pi IP
        self.pi_port = tk.StringVar(value="8080")
        self.pi_user = tk.StringVar(value="ls")  # Default Pi user (updated for your setup)
        self.pc_viewer_process = None
        self.pi_stream_process = None
        self.ssh_manager = None
        
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the user interface"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Camera System Launcher", 
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Configuration frame
        config_frame = ttk.LabelFrame(main_frame, text="Configuration", padding="10")
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
        
        # Launch button
        self.launch_btn = ttk.Button(button_frame, text="🚀 Launch Camera System", 
                                   command=self.launch_system, style="Accent.TButton")
        self.launch_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Stop button
        self.stop_btn = ttk.Button(button_frame, text="⏹️ Stop All", 
                                 command=self.stop_system, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Test connection button
        self.test_btn = ttk.Button(button_frame, text="🔍 Test Pi Connection", 
                                 command=self.test_pi_connection)
        self.test_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # Setup SSH Auth button
        self.setup_ssh_btn = ttk.Button(button_frame, text="🔐 Setup SSH Auth", 
                                      command=self.setup_ssh_authentication)
        self.setup_ssh_btn.pack(side=tk.LEFT)
        
        # Status frame
        status_frame = ttk.LabelFrame(main_frame, text="Status", padding="10")
        status_frame.pack(fill=tk.BOTH, expand=True)
        
        # Status text
        self.status_text = tk.Text(status_frame, height=10, width=50, wrap=tk.WORD)
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
        
        ttk.Button(quick_btn_frame, text="📱 Open Pi Stream in Browser", 
                  command=self.open_pi_browser).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(quick_btn_frame, text="🖥️ Open PC Viewer Only", 
                  command=self.open_pc_viewer_only).pack(side=tk.LEFT, padx=5)
        
    def log_message(self, message):
        """Log a message to the status text area"""
        timestamp = time.strftime("%H:%M:%S")
        self.status_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.status_text.see(tk.END)
        self.root.update_idletasks()
        
    def test_pi_connection(self):
        """Test connection to Raspberry Pi"""
        self.log_message("Testing connection to Raspberry Pi...")
        
        def test_connection():
            try:
                url = f"http://{self.pi_ip.get()}:{self.pi_port.get()}/status"
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    status = response.json()
                    self.root.after(0, lambda: self.log_message("✅ Pi connection successful!"))
                    self.root.after(0, lambda: self.log_message(f"   Camera available: {status.get('camera_available', 'Unknown')}"))
                    self.root.after(0, lambda: self.log_message(f"   Stream running: {status.get('running', 'Unknown')}"))
                else:
                    self.root.after(0, lambda: self.log_message(f"❌ Pi connection failed: HTTP {response.status_code}"))
            except Exception as e:
                error_msg = str(e)
                self.root.after(0, lambda: self.log_message(f"❌ Pi connection failed: {error_msg}"))
        
        # Run test in separate thread
        threading.Thread(target=test_connection, daemon=True).start()
    
    def setup_ssh_authentication(self):
        """Setup SSH key-based authentication"""
        self.log_message("🔐 Setting up SSH authentication...")
        self.log_message(f"   Using Pi IP: {self.pi_ip.get()}")
        self.log_message(f"   Using Pi User: {self.pi_user.get()}")
        
        def setup_auth():
            try:
                # Initialize SSH manager with current settings
                self.ssh_manager = SSHManager(self.pi_ip.get(), self.pi_user.get())
                
                # Setup complete authentication
                success = self.ssh_manager.setup_complete_authentication()
                
                if success:
                    self.root.after(0, lambda: self.log_message("✅ SSH authentication setup complete!"))
                    self.root.after(0, lambda: self.log_message("   No more password prompts!"))
                else:
                    self.root.after(0, lambda: self.log_message("❌ SSH authentication setup failed"))
                    self.root.after(0, lambda: self.log_message("   Check your Pi IP and username settings"))
                    
            except Exception as e:
                error_msg = str(e)
                self.root.after(0, lambda: self.log_message(f"❌ SSH setup error: {error_msg}"))
        
        # Run setup in separate thread
        threading.Thread(target=setup_auth, daemon=True).start()
    
    def ensure_ssh_manager(self):
        """Ensure SSH manager is initialized"""
        if not self.ssh_manager:
            self.ssh_manager = SSHManager(self.pi_ip.get(), self.pi_user.get())
        return self.ssh_manager
        
    def launch_system(self):
        """Launch the complete camera system"""
        self.log_message("🚀 Starting Camera System...")
        
        # Disable launch button and enable stop button
        self.launch_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        
        # Start Pi camera stream (if not already running)
        self.start_pi_stream()
        
        # Start PC camera viewer
        self.start_pc_viewer()
        
        # Open Pi stream in browser after a short delay
        self.root.after(3000, self.open_pi_browser)
        
    def start_pi_stream(self):
        """Start the Pi camera stream"""
        self.log_message("📡 Starting Pi camera stream...")
        
        def start_stream():
            try:
                # Check if stream is already running
                url = f"http://{self.pi_ip.get()}:{self.pi_port.get()}/status"
                response = requests.get(url, timeout=3)
                if response.status_code == 200:
                    self.root.after(0, lambda: self.log_message("✅ Pi camera stream already running"))
                    return
            except:
                pass
            
            # Try to start the stream on Pi using SSH
            try:
                ssh_manager = self.ensure_ssh_manager()
                
                # Check if SSH authentication is working
                if ssh_manager.test_key_authentication():
                    self.root.after(0, lambda: self.log_message("🔐 SSH authentication working"))
                    
                    # Try to start the camera service
                    success, stdout, stderr = ssh_manager.run_ssh_command("sudo systemctl start camera-stream.service")
                    if success:
                        self.root.after(0, lambda: self.log_message("✅ Started camera streaming service"))
                    else:
                        self.root.after(0, lambda: self.log_message("⚠️ Could not start service, trying manual start"))
                        # Try manual start
                        success, stdout, stderr = ssh_manager.run_ssh_command("cd ~/kinect_ws && python3 camera_streamer.py &")
                        if success:
                            self.root.after(0, lambda: self.log_message("✅ Started camera stream manually"))
                        else:
                            self.root.after(0, lambda: self.log_message(f"⚠️ Manual start failed: {stderr}"))
                else:
                    self.root.after(0, lambda: self.log_message("⚠️ SSH authentication not working"))
                    self.root.after(0, lambda: self.log_message("   Click 'Setup SSH Auth' to fix this"))
                    self.root.after(0, lambda: self.log_message("   Or start camera_streamer.py manually on your Pi"))
                    
            except Exception as e:
                error_msg = str(e)
                self.root.after(0, lambda: self.log_message(f"⚠️ Could not start Pi stream: {error_msg}"))
        
        threading.Thread(target=start_stream, daemon=True).start()
        
    def start_pc_viewer(self):
        """Start the PC camera viewer"""
        self.log_message("🖥️ Starting PC camera viewer...")
        
        try:
            # Get the directory of this script
            script_dir = os.path.dirname(os.path.abspath(__file__))
            viewer_script = os.path.join(script_dir, "windows_camera_viewer.py")
            
            if not os.path.exists(viewer_script):
                self.log_message("❌ PC viewer script not found!")
                return
            
            # Start the viewer process
            self.pc_viewer_process = subprocess.Popen([
                sys.executable, viewer_script
            ], cwd=script_dir)
            
            self.log_message("✅ PC camera viewer started")
            
        except Exception as e:
            self.log_message(f"❌ Failed to start PC viewer: {e}")
            
    def stop_system(self):
        """Stop all camera system components"""
        self.log_message("⏹️ Stopping camera system...")
        
        # Stop PC viewer
        if self.pc_viewer_process:
            try:
                self.pc_viewer_process.terminate()
                self.pc_viewer_process.wait(timeout=5)
                self.log_message("✅ PC camera viewer stopped")
            except:
                try:
                    self.pc_viewer_process.kill()
                    self.log_message("✅ PC camera viewer force stopped")
                except:
                    self.log_message("⚠️ Could not stop PC camera viewer")
            finally:
                self.pc_viewer_process = None
        
        # Try to stop Pi stream via SSH
        try:
            ssh_manager = self.ensure_ssh_manager()
            if ssh_manager.test_key_authentication():
                success, stdout, stderr = ssh_manager.run_ssh_command("sudo systemctl stop camera-stream.service")
                if success:
                    self.log_message("✅ Pi camera stream service stopped")
                else:
                    self.log_message("⚠️ Could not stop Pi service (may not be running)")
            else:
                self.log_message("ℹ️ Pi stream continues running (SSH auth not working)")
        except Exception as e:
            self.log_message(f"ℹ️ Pi stream continues running (error: {e})")
        
        # Re-enable launch button and disable stop button
        self.launch_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        
    def open_pi_browser(self):
        """Open Pi camera stream in browser"""
        url = f"http://{self.pi_ip.get()}:{self.pi_port.get()}"
        self.log_message(f"🌐 Opening Pi stream in browser: {url}")
        try:
            webbrowser.open(url)
        except Exception as e:
            self.log_message(f"❌ Could not open browser: {e}")
            
    def open_pc_viewer_only(self):
        """Open only the PC camera viewer"""
        self.log_message("🖥️ Opening PC camera viewer only...")
        self.start_pc_viewer()
        
    def on_closing(self):
        """Handle window closing"""
        if self.pc_viewer_process:
            self.stop_system()
        self.root.destroy()
        
    def run(self):
        """Run the launcher application"""
        self.log_message("🎯 Camera System Launcher ready!")
        self.log_message("Configure your Pi IP address and click 'Launch Camera System'")
        
        # Handle window closing
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Start the application
        self.root.mainloop()

def main():
    """Main function"""
    print("Starting Camera System Launcher...")
    
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
    launcher = CameraSystemLauncher()
    launcher.run()
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
