#!/usr/bin/env python3
"""
Simple real Kinect 360 video capture using system libfreenect with callbacks.
"""

import ctypes
import numpy as np
import cv2
import threading
import time
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Optional

class SimpleFreenect:
    """Simple freenect wrapper using callbacks."""
    
    def __init__(self):
        self.lib = None
        self.ctx = None
        self.device = None
        self._load_library()
        
        # Video data storage
        self.video_data = None
        self.depth_data = None
        self.video_lock = threading.Lock()
        self.depth_lock = threading.Lock()
        
    def _load_library(self):
        """Load the system libfreenect library."""
        try:
            self.lib = ctypes.CDLL('libfreenect.so.0.5')
            self._setup_function_signatures()
            print("✅ System libfreenect loaded successfully")
        except Exception as e:
            print(f"❌ Failed to load libfreenect: {e}")
            self.lib = None
    
    def _setup_function_signatures(self):
        """Setup function signatures for ctypes."""
        if not self.lib:
            return
            
        # freenect_init
        self.lib.freenect_init.argtypes = [ctypes.POINTER(ctypes.c_void_p), ctypes.c_void_p]
        self.lib.freenect_init.restype = ctypes.c_int
        
        # freenect_num_devices
        self.lib.freenect_num_devices.argtypes = [ctypes.c_void_p]
        self.lib.freenect_num_devices.restype = ctypes.c_int
        
        # freenect_open_device
        self.lib.freenect_open_device.argtypes = [ctypes.c_void_p, ctypes.c_int]
        self.lib.freenect_open_device.restype = ctypes.c_void_p
        
        # freenect_shutdown
        self.lib.freenect_shutdown.argtypes = [ctypes.c_void_p]
        self.lib.freenect_shutdown.restype = ctypes.c_int
        
        # freenect_set_video_mode
        self.lib.freenect_set_video_mode.argtypes = [ctypes.c_void_p, ctypes.c_int]
        self.lib.freenect_set_video_mode.restype = ctypes.c_int
        
        # freenect_set_depth_mode
        self.lib.freenect_set_depth_mode.argtypes = [ctypes.c_void_p, ctypes.c_int]
        self.lib.freenect_set_depth_mode.restype = ctypes.c_int
        
        # freenect_start_video
        self.lib.freenect_start_video.argtypes = [ctypes.c_void_p]
        self.lib.freenect_start_video.restype = ctypes.c_int
        
        # freenect_start_depth
        self.lib.freenect_start_depth.argtypes = [ctypes.c_void_p]
        self.lib.freenect_start_depth.restype = ctypes.c_int
        
        # freenect_stop_video
        self.lib.freenect_stop_video.argtypes = [ctypes.c_void_p]
        self.lib.freenect_stop_video.restype = ctypes.c_int
        
        # freenect_stop_depth
        self.lib.freenect_stop_depth.argtypes = [ctypes.c_void_p]
        self.lib.freenect_stop_depth.restype = ctypes.c_int
        
        # freenect_close_device
        self.lib.freenect_close_device.argtypes = [ctypes.c_void_p]
        self.lib.freenect_close_device.restype = ctypes.c_int
        
        # freenect_process_events
        self.lib.freenect_process_events.argtypes = [ctypes.c_void_p]
        self.lib.freenect_process_events.restype = ctypes.c_int
        
        # freenect_set_video_callback
        self.lib.freenect_set_video_callback.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
        self.lib.freenect_set_video_callback.restype = ctypes.c_int
        
        # freenect_set_depth_callback
        self.lib.freenect_set_depth_callback.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
        self.lib.freenect_set_depth_callback.restype = ctypes.c_int
    
    def _video_callback(self, device, data, timestamp):
        """Video callback function."""
        if data:
            # Convert raw data to numpy array (RGB format)
            video_ptr = ctypes.cast(data, ctypes.POINTER(ctypes.c_uint8))
            video_array = np.ctypeslib.as_array(video_ptr, shape=(480, 640, 3))
            
            with self.video_lock:
                self.video_data = video_array.copy()
    
    def _depth_callback(self, device, data, timestamp):
        """Depth callback function."""
        if data:
            # Convert raw data to numpy array
            depth_ptr = ctypes.cast(data, ctypes.POINTER(ctypes.c_uint16))
            depth_array = np.ctypeslib.as_array(depth_ptr, shape=(480, 640))
            
            with self.depth_lock:
                self.depth_data = depth_array.copy()
    
    def init(self) -> bool:
        """Initialize freenect context."""
        if not self.lib:
            return False
            
        self.ctx = ctypes.c_void_p()
        result = self.lib.freenect_init(ctypes.byref(self.ctx), None)
        return result == 0
    
    def num_devices(self) -> int:
        """Get number of devices."""
        if not self.lib or not self.ctx:
            return 0
        return self.lib.freenect_num_devices(self.ctx)
    
    def open_device(self, device_index: int = 0) -> bool:
        """Open a device."""
        if not self.lib or not self.ctx:
            return False
            
        self.device = self.lib.freenect_open_device(self.ctx, device_index)
        if not self.device:
            return False
        
        # Set video and depth modes
        # RGB video mode (640x480)
        self.lib.freenect_set_video_mode(self.device, 0)  # FREENECT_VIDEO_RGB
        # 11-bit depth mode (640x480)
        self.lib.freenect_set_depth_mode(self.device, 0)  # FREENECT_DEPTH_11BIT
        
        # Set up callbacks
        video_callback_type = ctypes.CFUNCTYPE(None, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_uint32)
        depth_callback_type = ctypes.CFUNCTYPE(None, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_uint32)
        
        self.video_callback = video_callback_type(self._video_callback)
        self.depth_callback = depth_callback_type(self._depth_callback)
        
        # Set callbacks
        self.lib.freenect_set_video_callback(self.device, self.video_callback)
        self.lib.freenect_set_depth_callback(self.device, self.depth_callback)
        
        # Start video and depth streams
        self.lib.freenect_start_video(self.device)
        self.lib.freenect_start_depth(self.device)
        
        return True
    
    def process_events(self):
        """Process freenect events."""
        if self.lib and self.ctx:
            self.lib.freenect_process_events(self.ctx)
    
    def get_video_frame(self) -> Optional[np.ndarray]:
        """Get the latest video frame."""
        with self.video_lock:
            return self.video_data.copy() if self.video_data is not None else None
    
    def get_depth_frame(self) -> Optional[np.ndarray]:
        """Get the latest depth frame."""
        with self.depth_lock:
            return self.depth_data.copy() if self.depth_data is not None else None
    
    def shutdown(self):
        """Shutdown freenect."""
        if self.device and self.lib:
            self.lib.freenect_stop_video(self.device)
            self.lib.freenect_stop_depth(self.device)
            self.lib.freenect_close_device(self.device)
            self.device = None
            
        if self.ctx and self.lib:
            self.lib.freenect_shutdown(self.ctx)
            self.ctx = None

class SimpleKinectStreamer:
    """Simple Kinect streamer with real video capture."""
    
    def __init__(self, host="0.0.0.0", port=8080):
        self.freenect = SimpleFreenect()
        self.running = False
        self.host = host
        self.port = port
        self.server = None
        self.frame_count = 0
        self.start_time = time.time()
        
    def start(self) -> bool:
        """Start the Kinect streamer."""
        print("🔍 Initializing Kinect...")
        
        if not self.freenect.init():
            print("❌ Failed to initialize freenect")
            return False
            
        device_count = self.freenect.num_devices()
        print(f"✅ Found {device_count} Kinect devices")
        
        if device_count == 0:
            print("❌ No Kinect devices found")
            return False
            
        if not self.freenect.open_device(0):
            print("❌ Failed to open Kinect device")
            return False
            
        print("✅ Kinect device opened successfully")
        print("🎥 Starting real video capture...")
        
        self.running = True
        
        # Start capture thread
        self.capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.capture_thread.start()
        
        # Start HTTP server
        self._start_http_server()
        
        return True
    
    def _capture_loop(self):
        """Real capture loop."""
        print("🎥 Starting real video capture loop...")
        
        while self.running:
            # Process freenect events to get new frames
            self.freenect.process_events()
            
            # Get real video frame
            video_frame = self.freenect.get_video_frame()
            if video_frame is not None:
                self.frame_count += 1
                
                # Print status every 100 frames
                if self.frame_count % 100 == 0:
                    elapsed = time.time() - self.start_time
                    fps = self.frame_count / (elapsed + 0.001)
                    print(f"📹 Captured {self.frame_count} real frames (FPS: {fps:.1f})")
            
            time.sleep(1.0 / 30.0)  # 30 FPS
    
    def get_frame(self) -> Optional[np.ndarray]:
        """Get the latest real video frame."""
        return self.freenect.get_video_frame()
    
    def get_depth_frame(self) -> Optional[np.ndarray]:
        """Get the latest depth frame."""
        return self.freenect.get_depth_frame()
    
    def _start_http_server(self):
        """Start HTTP server."""
        handler = lambda *args: SimpleKinectHTTPHandler(self, *args)
        
        try:
            self.server = HTTPServer((self.host, self.port), handler)
            print(f"✅ HTTP server started on http://{self.host}:{self.port}")
            print("Available endpoints:")
            print("  / - Camera viewer")
            print("  /stream - Raw video stream")
            print("  /depth - Depth stream")
            print("  /status - Server status")
            
            # Start server in a separate thread
            server_thread = threading.Thread(target=self.server.serve_forever, daemon=True)
            server_thread.start()
            
        except Exception as e:
            print(f"❌ Failed to start HTTP server: {e}")
    
    def stop(self):
        """Stop the streamer."""
        print("🛑 Stopping Kinect streamer...")
        self.running = False
        
        if self.server:
            self.server.shutdown()
            self.server = None
        
        if hasattr(self, 'capture_thread'):
            self.capture_thread.join(timeout=5.0)
            
        self.freenect.shutdown()
        print("✅ Kinect streamer stopped")

class SimpleKinectHTTPHandler(BaseHTTPRequestHandler):
    """HTTP request handler for simple Kinect streaming."""
    
    def __init__(self, streamer, *args, **kwargs):
        self.streamer = streamer
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """Handle GET requests."""
        if self.path == '/':
            self._serve_html()
        elif self.path == '/stream':
            self._serve_stream()
        elif self.path == '/depth':
            self._serve_depth_stream()
        elif self.path == '/status':
            self._serve_status()
        else:
            self.send_error(404)
    
    def _serve_html(self):
        """Serve the camera viewer HTML page."""
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Real Kinect 360 Stream</title>
            <style>
                body { 
                    font-family: Arial, sans-serif; 
                    text-align: center; 
                    background-color: #f0f0f0;
                    margin: 0;
                    padding: 20px;
                }
                .container {
                    max-width: 1200px;
                    margin: 0 auto;
                    background: white;
                    padding: 20px;
                    border-radius: 10px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }
                h1 { color: #333; }
                .streams {
                    display: flex;
                    gap: 20px;
                    justify-content: center;
                    flex-wrap: wrap;
                }
                .stream-container {
                    text-align: center;
                }
                .stream-container h3 {
                    margin: 10px 0;
                    color: #555;
                }
                #video, #depth { 
                    max-width: 100%; 
                    height: auto; 
                    border: 2px solid #ddd;
                    border-radius: 5px;
                }
                .status { margin: 10px 0; color: #666; }
                .info { 
                    background: #e7f3ff; 
                    padding: 15px; 
                    border-radius: 5px; 
                    margin: 20px 0;
                    border-left: 4px solid #007bff;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🎯 Real Kinect 360 Camera Stream</h1>
                <div class="info">
                    <strong>✅ Real Kinect 360 Video Capture Active!</strong><br>
                    Capturing actual video from Kinect hardware using system libfreenect.
                </div>
                <div class="status" id="status">Connecting...</div>
                
                <div class="streams">
                    <div class="stream-container">
                        <h3>RGB Video</h3>
                        <img id="video" src="/stream" alt="RGB Feed">
                    </div>
                    <div class="stream-container">
                        <h3>Depth Video</h3>
                        <img id="depth" src="/depth" alt="Depth Feed">
                    </div>
                </div>
            </div>
            
            <script>
                let videoImg = document.getElementById('video');
                let depthImg = document.getElementById('depth');
                let status = document.getElementById('status');
                
                function updateStatus(message, isError = false) {
                    status.textContent = message;
                    status.style.color = isError ? '#dc3545' : '#28a745';
                }
                
                function onImageLoad() {
                    updateStatus('✅ Real Kinect 360 streams connected successfully');
                }
                
                function onImageError() {
                    updateStatus('❌ Stream connection failed', true);
                }
                
                videoImg.onload = onImageLoad;
                videoImg.onerror = onImageError;
                depthImg.onload = onImageLoad;
                depthImg.onerror = onImageError;
                
                // Auto-refresh every 30 seconds
                setInterval(() => {
                    videoImg.src = '/stream?' + new Date().getTime();
                    depthImg.src = '/depth?' + new Date().getTime();
                }, 30000);
            </script>
        </body>
        </html>
        """
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())
    
    def _serve_stream(self):
        """Serve the real video stream."""
        frame = self.streamer.get_frame()
        if frame is None:
            # Create a placeholder frame
            frame = np.zeros((480, 640, 3), dtype=np.uint8)
            frame[:] = (50, 0, 0)  # Dark red
            cv2.putText(frame, "Waiting for video...", (200, 240), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)
        
        # Encode frame as JPEG
        _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
        
        self.send_response(200)
        self.send_header('Content-type', 'image/jpeg')
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        self.end_headers()
        self.wfile.write(buffer.tobytes())
    
    def _serve_depth_stream(self):
        """Serve the depth stream."""
        depth_frame = self.streamer.get_depth_frame()
        if depth_frame is None:
            # Create a placeholder depth frame
            frame = np.zeros((480, 640, 3), dtype=np.uint8)
            frame[:] = (50, 50, 50)  # Dark gray
            cv2.putText(frame, "Waiting for depth...", (200, 240), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)
        else:
            # Convert depth to colorized image
            depth_normalized = cv2.normalize(depth_frame, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
            frame = cv2.applyColorMap(depth_normalized, cv2.COLORMAP_JET)
        
        # Encode frame as JPEG
        _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
        
        self.send_response(200)
        self.send_header('Content-type', 'image/jpeg')
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        self.end_headers()
        self.wfile.write(buffer.tobytes())
    
    def _serve_status(self):
        """Serve server status."""
        elapsed = time.time() - self.streamer.start_time
        fps = self.streamer.frame_count / (elapsed + 0.001)
        
        status = {
            'running': self.streamer.running,
            'frame_count': self.streamer.frame_count,
            'fps': fps,
            'elapsed_time': elapsed,
            'kinect_available': True,
            'kinect_method': 'simple_system_freenect',
            'video_available': self.streamer.get_frame() is not None,
            'depth_available': self.streamer.get_depth_frame() is not None,
            'timestamp': time.time()
        }
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(status).encode())
    
    def log_message(self, format, *args):
        """Suppress default logging."""
        pass

# Main execution
if __name__ == "__main__":
    streamer = SimpleKinectStreamer(host="0.0.0.0", port=8080)
    
    try:
        if streamer.start():
            print("✅ Simple Kinect streamer started successfully")
            print("🌐 Open http://192.168.1.9:8080 in your browser")
            print("Press Ctrl+C to stop")
            
            # Keep running
            while True:
                time.sleep(1)
        else:
            print("❌ Failed to start Kinect streamer")
    except KeyboardInterrupt:
        print("\n🛑 Stopping...")
        streamer.stop()
