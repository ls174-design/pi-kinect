#!/usr/bin/env python3
"""
Windows camera viewer client
Connects to Raspberry Pi camera stream and displays it in a window
"""

import tkinter as tk
from tkinter import ttk, messagebox
import requests
import threading
import time
from PIL import Image, ImageTk
import io
import json

class CameraViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("Raspberry Pi Camera Viewer")
        self.root.geometry("800x600")
        
        # Configuration
        self.pi_ip = tk.StringVar(value="192.168.1.9")  # Default Pi IP
        self.pi_port = tk.StringVar(value="8080")
        self.streaming = False
        self.current_image = None
        
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the user interface"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Connection settings
        ttk.Label(main_frame, text="Raspberry Pi IP:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ip_entry = ttk.Entry(main_frame, textvariable=self.pi_ip, width=20)
        ip_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(5, 0), pady=5)
        
        ttk.Label(main_frame, text="Port:").grid(row=0, column=2, sticky=tk.W, padx=(10, 0), pady=5)
        port_entry = ttk.Entry(main_frame, textvariable=self.pi_port, width=10)
        port_entry.grid(row=0, column=3, sticky=tk.W, padx=(5, 0), pady=5)
        
        # Control buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=1, column=0, columnspan=4, pady=10)
        
        self.connect_btn = ttk.Button(button_frame, text="Connect", command=self.toggle_connection)
        self.connect_btn.pack(side=tk.LEFT, padx=5)
        
        self.refresh_btn = ttk.Button(button_frame, text="Refresh", command=self.refresh_stream)
        self.refresh_btn.pack(side=tk.LEFT, padx=5)
        
        self.capture_btn = ttk.Button(button_frame, text="Capture", command=self.capture_frame)
        self.capture_btn.pack(side=tk.LEFT, padx=5)
        
        # Status label
        self.status_label = ttk.Label(main_frame, text="Disconnected", foreground="red")
        self.status_label.grid(row=1, column=0, columnspan=4, pady=5)
        
        # Image display
        self.image_label = ttk.Label(main_frame, text="No image", anchor="center")
        self.image_label.grid(row=2, column=0, columnspan=4, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        # Info frame
        info_frame = ttk.LabelFrame(main_frame, text="Stream Info", padding="5")
        info_frame.grid(row=3, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=10)
        
        self.info_text = tk.Text(info_frame, height=4, width=60)
        self.info_text.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar for info text
        scrollbar = ttk.Scrollbar(info_frame, orient=tk.VERTICAL, command=self.info_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.info_text.configure(yscrollcommand=scrollbar.set)
        
    def get_stream_url(self):
        """Get the stream URL"""
        return f"http://{self.pi_ip.get()}:{self.pi_port.get()}/stream"
    
    def get_status_url(self):
        """Get the status URL"""
        return f"http://{self.pi_ip.get()}:{self.pi_port.get()}/status"
    
    def update_status(self, message, color="black"):
        """Update status label"""
        self.status_label.config(text=message, foreground=color)
        self.root.update_idletasks()
    
    def log_info(self, message):
        """Log information to the info text area"""
        timestamp = time.strftime("%H:%M:%S")
        self.info_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.info_text.see(tk.END)
        self.root.update_idletasks()
    
    def check_connection(self):
        """Check if the Pi camera stream is available"""
        try:
            response = requests.get(self.get_status_url(), timeout=5)
            if response.status_code == 200:
                status = response.json()
                return True, status
            else:
                return False, None
        except Exception as e:
            return False, str(e)
    
    def check_stream_endpoint(self):
        """Check if the stream endpoint is working and what type of data it serves"""
        try:
            response = requests.get(self.get_stream_url(), timeout=5)
            if response.status_code == 200:
                content_type = response.headers.get('Content-Type', '')
                content_length = len(response.content)
                
                # Check if it's actually image data or status frame
                if 'image/' in content_type:
                    # Try to decode as image to see if it's real camera data
                    try:
                        from PIL import Image
                        import io
                        image = Image.open(io.BytesIO(response.content))
                        # Check if it's a status frame (dark green background)
                        # by sampling a few pixels
                        pixels = list(image.getdata())
                        if len(pixels) > 1000:
                            # Sample some pixels to detect status frame
                            sample_pixels = pixels[::len(pixels)//100]  # Sample 100 pixels
                            green_pixels = sum(1 for r, g, b in sample_pixels if g > r and g > b and g > 100)
                            # Check for text patterns that indicate status frame
                            has_text_pattern = any(
                                (r, g, b) == (0, 255, 0) or (r, g, b) == (255, 255, 255) 
                                for r, g, b in sample_pixels
                            )
                            if green_pixels > 50 and has_text_pattern:  # Mostly green pixels with text = status frame
                                return True, "status_frame", content_length
                            else:
                                return True, "real_camera", content_length
                        else:
                            return True, "unknown", content_length
                    except Exception as img_e:
                        return True, "image_decode_error", content_length
                else:
                    return True, "non_image", content_length
            else:
                return False, f"HTTP {response.status_code}", 0
        except Exception as e:
            return False, str(e), 0
    
    def toggle_connection(self):
        """Toggle camera stream connection"""
        if self.streaming:
            self.stop_streaming()
        else:
            self.start_streaming()
    
    def start_streaming(self):
        """Start camera streaming"""
        self.update_status("Connecting...", "orange")
        self.log_info("Attempting to connect to Raspberry Pi...")
        
        # Check connection
        connected, status = self.check_connection()
        if not connected:
            self.update_status("Connection failed", "red")
            self.log_info(f"Failed to connect: {status}")
            messagebox.showerror("Connection Error", f"Could not connect to Raspberry Pi at {self.pi_ip.get()}:{self.pi_port.get()}")
            return
        
        # Check what type of stream we're getting
        stream_working, stream_type, content_size = self.check_stream_endpoint()
        if not stream_working:
            self.update_status("Stream endpoint failed", "red")
            self.log_info(f"Stream endpoint error: {stream_type}")
            messagebox.showerror("Stream Error", f"Stream endpoint not working: {stream_type}")
            return
        
        self.streaming = True
        self.connect_btn.config(text="Disconnect")
        
        # Determine status based on stream type
        if stream_type == "status_frame":
            self.update_status("Connected (Status Only)", "orange")
            self.log_info("⚠️ WARNING: Connected to status frame, not real camera data")
            self.log_info("The server is running but no real camera/Kinect is available")
        elif stream_type == "real_camera":
            self.update_status("Connected", "green")
            self.log_info("✅ Successfully connected to real camera stream")
        else:
            self.update_status("Connected (Unknown)", "orange")
            self.log_info(f"Connected but stream type unknown: {stream_type}")
        
        if isinstance(status, dict):
            self.log_info(f"Camera available: {status.get('camera_available', 'Unknown')}")
            self.log_info(f"Frame available: {status.get('frame_available', 'Unknown')}")
            if 'kinect_available' in status:
                self.log_info(f"Kinect available: {status.get('kinect_available', 'Unknown')}")
                self.log_info(f"Kinect method: {status.get('kinect_method', 'Unknown')}")
        
        self.log_info(f"Stream content size: {content_size} bytes")
        
        # Start streaming thread
        self.stream_thread = threading.Thread(target=self.stream_loop, daemon=True)
        self.stream_thread.start()
    
    def stop_streaming(self):
        """Stop camera streaming"""
        self.streaming = False
        self.connect_btn.config(text="Connect")
        self.update_status("Disconnected", "red")
        self.log_info("Disconnected from camera stream")
        self.image_label.config(image="", text="No image")
    
    def stream_loop(self):
        """Main streaming loop"""
        while self.streaming:
            try:
                response = requests.get(self.get_stream_url(), timeout=10)
                if response.status_code == 200:
                    # Convert response to image
                    image = Image.open(io.BytesIO(response.content))
                    
                    # Resize image to fit window
                    window_width = self.root.winfo_width() - 50
                    window_height = self.root.winfo_height() - 200
                    
                    if window_width > 100 and window_height > 100:
                        image.thumbnail((window_width, window_height), Image.Resampling.LANCZOS)
                    
                    # Convert to PhotoImage
                    photo = ImageTk.PhotoImage(image)
                    
                    # Update image in main thread
                    self.root.after(0, self.update_image, photo)
                    
                else:
                    self.log_info(f"Stream error: HTTP {response.status_code}")
                    
            except Exception as e:
                self.log_info(f"Stream error: {e}")
                if self.streaming:
                    self.root.after(0, self.handle_stream_error)
            
            time.sleep(0.1)  # 10 FPS update rate
    
    def update_image(self, photo):
        """Update the displayed image (called from main thread)"""
        if self.streaming:
            self.image_label.config(image=photo, text="")
            self.current_image = photo  # Keep reference to prevent garbage collection
    
    def handle_stream_error(self):
        """Handle streaming errors"""
        self.log_info("Stream connection lost, attempting to reconnect...")
        time.sleep(2)
    
    def refresh_stream(self):
        """Refresh the stream"""
        if self.streaming:
            self.log_info("Refreshing stream...")
            # The stream loop will automatically get the latest frame
        else:
            self.log_info("Not connected to stream")
    
    def capture_frame(self):
        """Capture current frame"""
        if not self.streaming or not self.current_image:
            messagebox.showwarning("No Image", "No image to capture. Please connect to the stream first.")
            return
        
        try:
            # Get current frame from stream
            response = requests.get(self.get_stream_url(), timeout=5)
            if response.status_code == 200:
                # Save image
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                filename = f"camera_capture_{timestamp}.jpg"
                
                with open(filename, 'wb') as f:
                    f.write(response.content)
                
                self.log_info(f"Frame captured: {filename}")
                messagebox.showinfo("Capture Success", f"Frame saved as {filename}")
            else:
                messagebox.showerror("Capture Error", f"Failed to capture frame: HTTP {response.status_code}")
                
        except Exception as e:
            messagebox.showerror("Capture Error", f"Failed to capture frame: {e}")
    
    def on_closing(self):
        """Handle window closing"""
        if self.streaming:
            self.stop_streaming()
        self.root.destroy()

def main():
    root = tk.Tk()
    app = CameraViewer(root)
    
    # Handle window closing
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    # Start the application
    root.mainloop()

if __name__ == '__main__':
    main()
