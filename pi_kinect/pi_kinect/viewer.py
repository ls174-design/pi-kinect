"""
GUI camera viewer for Pi-Kinect.

Provides a Tkinter-based viewer for connecting to and displaying
camera streams from a Raspberry Pi.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import requests
import threading
import time
from PIL import Image, ImageTk
import io
import json
from typing import Optional, Callable

from .config import Config
from .logging_config import LoggerMixin, get_logger
from .exceptions import NetworkError, StreamError


class CameraViewer(LoggerMixin):
    """
    GUI camera viewer for Pi-Kinect streams.
    
    Features:
    - Real-time camera stream display
    - Connection management with status monitoring
    - Frame capture and saving
    - Configurable Pi connection settings
    - Proper error handling and user feedback
    """
    
    def __init__(self, root: tk.Tk, config: Config):
        """
        Initialize the camera viewer.
        
        Args:
            root: Tkinter root window
            config: Configuration object
        """
        self.root = root
        self.config = config
        self.logger = get_logger(__name__)
        
        # Connection state
        self.streaming = False
        self.current_image: Optional[ImageTk.PhotoImage] = None
        
        # UI components
        self.pi_ip_var = tk.StringVar(value=config.pi_ip)
        self.pi_port_var = tk.StringVar(value=str(config.network.port))
        self.status_label: Optional[ttk.Label] = None
        self.image_label: Optional[ttk.Label] = None
        self.info_label: Optional[ttk.Label] = None
        
        # Control buttons
        self.connect_button: Optional[ttk.Button] = None
        self.disconnect_button: Optional[ttk.Button] = None
        self.capture_button: Optional[ttk.Button] = None
        
        self.setup_ui()
    
    def setup_ui(self) -> None:
        """Set up the user interface."""
        self.root.title("Pi-Kinect Camera Viewer")
        self.root.geometry("800x600")
        
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Connection settings
        ttk.Label(main_frame, text="Raspberry Pi IP:").grid(
            row=0, column=0, sticky=tk.W, pady=5
        )
        ip_entry = ttk.Entry(main_frame, textvariable=self.pi_ip_var, width=20)
        ip_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(5, 0), pady=5)
        
        ttk.Label(main_frame, text="Port:").grid(
            row=0, column=2, sticky=tk.W, padx=(10, 0), pady=5
        )
        port_entry = ttk.Entry(main_frame, textvariable=self.pi_port_var, width=10)
        port_entry.grid(row=0, column=3, sticky=tk.W, padx=(5, 0), pady=5)
        
        # Control buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=1, column=0, columnspan=4, pady=10)
        
        self.connect_button = ttk.Button(
            button_frame, text="Connect", command=self.connect
        )
        self.connect_button.grid(row=0, column=0, padx=5)
        
        self.disconnect_button = ttk.Button(
            button_frame, text="Disconnect", command=self.disconnect, state="disabled"
        )
        self.disconnect_button.grid(row=0, column=1, padx=5)
        
        self.capture_button = ttk.Button(
            button_frame, text="Capture Frame", command=self.capture_frame, state="disabled"
        )
        self.capture_button.grid(row=0, column=2, padx=5)
        
        # Status label
        self.status_label = ttk.Label(
            main_frame, text="Status: Disconnected", foreground="red"
        )
        self.status_label.grid(row=2, column=0, columnspan=4, pady=5)
        
        # Image display
        self.image_label = ttk.Label(
            main_frame, text="No image", background="lightgray", anchor="center"
        )
        self.image_label.grid(
            row=3, column=0, columnspan=4, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10
        )
        
        # Info frame
        info_frame = ttk.LabelFrame(main_frame, text="Stream Information", padding="5")
        info_frame.grid(row=4, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=5)
        
        self.info_label = ttk.Label(
            info_frame, text="No stream information available"
        )
        self.info_label.grid(row=0, column=0, sticky=tk.W)
    
    def connect(self) -> None:
        """Connect to the camera stream."""
        try:
            pi_ip = self.pi_ip_var.get()
            pi_port = self.pi_port_var.get()
            
            # Validate inputs
            if not pi_ip or not pi_port:
                messagebox.showerror("Error", "Please enter both IP address and port")
                return
            
            try:
                pi_port = int(pi_port)
            except ValueError:
                messagebox.showerror("Error", "Port must be a number")
                return
            
            # Test connection
            self._update_status("Testing connection...", "orange")
            self.root.update()
            
            # Test if the stream is available
            test_url = f"http://{pi_ip}:{pi_port}/status"
            response = requests.get(test_url, timeout=self.config.network.timeout)
            
            if response.status_code == 200:
                self._update_status("Connected", "green")
                self.connect_button.config(state="disabled")
                self.disconnect_button.config(state="normal")
                self.capture_button.config(state="normal")
                
                # Start streaming
                self.streaming = True
                self.start_streaming()
                
                # Update info
                try:
                    status_data = response.json()
                    info_text = (
                        f"Stream: {pi_ip}:{pi_port} | "
                        f"Status: {status_data.get('status', 'Unknown')}"
                    )
                    self.info_label.config(text=info_text)
                except:
                    self.info_label.config(text=f"Stream: {pi_ip}:{pi_port}")
                    
            else:
                self._update_status(f"Server error ({response.status_code})", "red")
                messagebox.showerror(
                    "Connection Error", 
                    f"Server returned status code: {response.status_code}"
                )
                
        except requests.exceptions.ConnectTimeout:
            self._update_status("Connection timeout", "red")
            messagebox.showerror(
                "Connection Error", 
                "Connection timeout. Please check:\n"
                "- Pi is powered on\n"
                "- Pi IP address is correct\n"
                "- Streaming service is running"
            )
        except requests.exceptions.ConnectionError:
            self._update_status("Connection refused", "red")
            messagebox.showerror(
                "Connection Error", 
                "Connection refused. Please check:\n"
                "- Pi is powered on\n"
                "- Streaming service is running\n"
                "- Port is correct"
            )
        except Exception as e:
            self._update_status("Connection failed", "red")
            messagebox.showerror("Connection Error", f"Failed to connect: {e}")
    
    def disconnect(self) -> None:
        """Disconnect from the camera stream."""
        self.streaming = False
        self._update_status("Disconnected", "red")
        self.connect_button.config(state="normal")
        self.disconnect_button.config(state="disabled")
        self.capture_button.config(state="disabled")
        self.image_label.config(image="", text="No image")
        self.info_label.config(text="No stream information available")
    
    def start_streaming(self) -> None:
        """Start the streaming thread."""
        def stream_thread():
            while self.streaming:
                try:
                    pi_ip = self.pi_ip_var.get()
                    pi_port = self.pi_port_var.get()
                    
                    # Get frame from stream
                    stream_url = f"http://{pi_ip}:{pi_port}/stream"
                    response = requests.get(
                        stream_url, 
                        timeout=self.config.network.timeout, 
                        stream=True
                    )
                    
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
                            max_width, max_height = 640, 480
                            if image.width > max_width or image.height > max_height:
                                image.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
                            
                            # Convert to PhotoImage
                            photo = ImageTk.PhotoImage(image)
                            
                            # Update the display
                            self.root.after(0, lambda: self.update_image(photo))
                            
                    else:
                        self.root.after(0, lambda: self._update_status(
                            f"Stream error ({response.status_code})", "red"
                        ))
                        
                except Exception as e:
                    if self.streaming:  # Only show error if we're still trying to stream
                        self.root.after(0, lambda: self._update_status(
                            f"Stream error - {str(e)[:50]}...", "red"
                        ))
                
                time.sleep(0.1)  # Small delay to prevent overwhelming the system
        
        threading.Thread(target=stream_thread, daemon=True).start()
    
    def update_image(self, photo: ImageTk.PhotoImage) -> None:
        """Update the displayed image."""
        self.current_image = photo  # Keep a reference
        self.image_label.config(image=photo, text="")
    
    def capture_frame(self) -> None:
        """Capture and save the current frame."""
        if self.current_image:
            try:
                # Generate filename with timestamp
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                filename = f"camera_capture_{timestamp}.jpg"
                
                # Get fresh frame for capture
                pi_ip = self.pi_ip_var.get()
                pi_port = self.pi_port_var.get()
                
                capture_url = f"http://{pi_ip}:{pi_port}/frame"
                response = requests.get(capture_url, timeout=self.config.network.timeout)
                
                if response.status_code == 200:
                    with open(filename, 'wb') as f:
                        f.write(response.content)
                    
                    messagebox.showinfo("Capture Success", f"Frame saved as: {filename}")
                else:
                    messagebox.showerror(
                        "Capture Error", 
                        f"Failed to capture frame: {response.status_code}"
                    )
                    
            except Exception as e:
                messagebox.showerror("Capture Error", f"Failed to save frame: {e}")
        else:
            messagebox.showwarning("No Image", "No image to capture")
    
    def _update_status(self, message: str, color: str = "black") -> None:
        """Update the status label."""
        self.status_label.config(text=f"Status: {message}", foreground=color)
    
    def stop(self) -> None:
        """Stop the viewer and cleanup resources."""
        self.streaming = False
        self.logger.info("Camera viewer stopped")


def main():
    """Main function for standalone viewer execution."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Pi-Kinect Camera Viewer")
    parser.add_argument("--pi-ip", default="192.168.1.9", help="Pi IP address")
    parser.add_argument("--pi-port", type=int, default=8080, help="Pi port")
    parser.add_argument("--config", help="Configuration file")
    
    args = parser.parse_args()
    
    # Load configuration
    config = Config.load(args.config)
    config.pi_ip = args.pi_ip
    config.network.port = args.pi_port
    
    # Setup logging
    from .logging_config import setup_logging
    setup_logging(config.logging)
    
    # Create and run viewer
    root = tk.Tk()
    app = CameraViewer(root, config)
    
    def on_closing():
        app.stop()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()
