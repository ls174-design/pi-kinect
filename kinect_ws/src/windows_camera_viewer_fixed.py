#!/usr/bin/env python3
"""
Windows camera viewer client - Fixed version
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
        
        self.connect_button = ttk.Button(button_frame, text="Connect", command=self.connect)
        self.connect_button.grid(row=0, column=0, padx=5)
        
        self.disconnect_button = ttk.Button(button_frame, text="Disconnect", 
                                          command=self.disconnect, state="disabled")
        self.disconnect_button.grid(row=0, column=1, padx=5)
        
        self.capture_button = ttk.Button(button_frame, text="Capture Frame", 
                                       command=self.capture_frame, state="disabled")
        self.capture_button.grid(row=0, column=2, padx=5)
        
        # Status label
        self.status_label = ttk.Label(main_frame, text="Status: Disconnected", foreground="red")
        self.status_label.grid(row=2, column=0, columnspan=4, pady=5)
        
        # Image display
        self.image_label = ttk.Label(main_frame, text="No image", 
                                   background="lightgray", anchor="center")
        self.image_label.grid(row=3, column=0, columnspan=4, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        # Info frame
        info_frame = ttk.LabelFrame(main_frame, text="Stream Information", padding="5")
        info_frame.grid(row=4, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=5)
        
        self.info_label = ttk.Label(info_frame, text="No stream information available")
        self.info_label.grid(row=0, column=0, sticky=tk.W)
        
    def connect(self):
        """Connect to the camera stream"""
        try:
            pi_ip = self.pi_ip.get()
            pi_port = self.pi_port.get()
            
            # Test connection
            self.status_label.config(text="Status: Testing connection...", foreground="orange")
            self.root.update()
            
            # Test if the stream is available
            test_url = f"http://{pi_ip}:{pi_port}/status"
            response = requests.get(test_url, timeout=5)
            
            if response.status_code == 200:
                self.status_label.config(text="Status: Connected", foreground="green")
                self.connect_button.config(state="disabled")
                self.disconnect_button.config(state="normal")
                self.capture_button.config(state="normal")
                
                # Start streaming
                self.streaming = True
                self.start_streaming()
                
                # Update info
                try:
                    status_data = response.json()
                    info_text = f"Stream: {pi_ip}:{pi_port} | Status: {status_data.get('status', 'Unknown')}"
                    self.info_label.config(text=info_text)
                except:
                    self.info_label.config(text=f"Stream: {pi_ip}:{pi_port}")
                    
            else:
                self.status_label.config(text=f"Status: Server error ({response.status_code})", foreground="red")
                messagebox.showerror("Connection Error", 
                                   f"Server returned status code: {response.status_code}")
                
        except requests.exceptions.ConnectTimeout:
            self.status_label.config(text="Status: Connection timeout", foreground="red")
            messagebox.showerror("Connection Error", 
                               "Connection timeout. Please check:\n- Pi is powered on\n- Pi IP address is correct\n- Streaming service is running")
        except requests.exceptions.ConnectionError:
            self.status_label.config(text="Status: Connection refused", foreground="red")
            messagebox.showerror("Connection Error", 
                               "Connection refused. Please check:\n- Pi is powered on\n- Streaming service is running\n- Port is correct")
        except Exception as e:
            self.status_label.config(text="Status: Connection failed", foreground="red")
            messagebox.showerror("Connection Error", f"Failed to connect: {e}")
    
    def disconnect(self):
        """Disconnect from the camera stream"""
        self.streaming = False
        self.status_label.config(text="Status: Disconnected", foreground="red")
        self.connect_button.config(state="normal")
        self.disconnect_button.config(state="disabled")
        self.capture_button.config(state="disabled")
        self.image_label.config(image="", text="No image")
        self.info_label.config(text="No stream information available")
    
    def start_streaming(self):
        """Start the streaming thread"""
        def stream_thread():
            while self.streaming:
                try:
                    pi_ip = self.pi_ip.get()
                    pi_port = self.pi_port.get()
                    
                    # Get frame from stream
                    stream_url = f"http://{pi_ip}:{pi_port}/stream"
                    response = requests.get(stream_url, timeout=10, stream=True)
                    
                    if response.status_code == 200:
                        # Read the image data
                        image_data = b""
                        for chunk in response.iter_content(chunk_size=1024):
                            if not self.streaming:
                                break
                            image_data += chunk
                        
                        if image_data:
                            # Convert to PIL Image
                            image = Image.open(io.BytesIO(image_data))
                            
                            # Resize if too large
                            if image.width > 640 or image.height > 480:
                                image.thumbnail((640, 480), Image.Resampling.LANCZOS)
                            
                            # Convert to PhotoImage
                            photo = ImageTk.PhotoImage(image)
                            
                            # Update the display
                            self.root.after(0, lambda: self.update_image(photo))
                            
                    else:
                        self.root.after(0, lambda: self.status_label.config(
                            text=f"Status: Stream error ({response.status_code})", foreground="red"))
                        
                except Exception as e:
                    if self.streaming:  # Only show error if we're still trying to stream
                        self.root.after(0, lambda: self.status_label.config(
                            text=f"Status: Stream error - {str(e)[:50]}...", foreground="red"))
                
                time.sleep(0.1)  # Small delay to prevent overwhelming the system
        
        threading.Thread(target=stream_thread, daemon=True).start()
    
    def update_image(self, photo):
        """Update the displayed image"""
        self.current_image = photo  # Keep a reference
        self.image_label.config(image=photo, text="")
    
    def capture_frame(self):
        """Capture and save the current frame"""
        if self.current_image:
            try:
                # Generate filename with timestamp
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                filename = f"camera_capture_{timestamp}.jpg"
                
                # Save the image
                pi_ip = self.pi_ip.get()
                pi_port = self.pi_port.get()
                
                # Get fresh frame for capture
                capture_url = f"http://{pi_ip}:{pi_port}/frame"
                response = requests.get(capture_url, timeout=5)
                
                if response.status_code == 200:
                    with open(filename, 'wb') as f:
                        f.write(response.content)
                    
                    messagebox.showinfo("Capture Success", f"Frame saved as: {filename}")
                else:
                    messagebox.showerror("Capture Error", f"Failed to capture frame: {response.status_code}")
                    
            except Exception as e:
                messagebox.showerror("Capture Error", f"Failed to save frame: {e}")
        else:
            messagebox.showwarning("No Image", "No image to capture")

def main():
    """Main function"""
    root = tk.Tk()
    app = CameraViewer(root)
    
    # Handle window close
    def on_closing():
        app.streaming = False
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == '__main__':
    main()
