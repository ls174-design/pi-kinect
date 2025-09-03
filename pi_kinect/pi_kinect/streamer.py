"""
Kinect streaming server with automatic device detection and fallback.

Provides a robust streaming solution that automatically detects and uses
the best available camera method (freenect, OpenCV) with proper error handling.
"""

import cv2
import numpy as np
import threading
import time
import base64
import json
import signal
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Optional, Tuple, Dict, Any
from queue import Queue, Empty
from pathlib import Path

from .config import Config
from .logging_config import LoggerMixin, get_logger
from .exceptions import (
    PiKinectError, DeviceNotFoundError, StreamError, 
    FreenectError, OpenCVError
)

# Try to import freenect for advanced Kinect support
try:
    import freenect
    FREENECT_AVAILABLE = True
except ImportError:
    FREENECT_AVAILABLE = False


class KinectStreamer(LoggerMixin):
    """
    Unified Kinect streaming server with automatic device detection.
    
    Features:
    - Automatic Kinect detection using multiple methods
    - Fallback to OpenCV if Kinect unavailable
    - Thread-safe frame capture and serving
    - HTTP-based streaming with REST API
    - Proper resource cleanup and error handling
    """
    
    def __init__(self, config: Config):
        """
        Initialize the Kinect streamer.
        
        Args:
            config: Configuration object
        """
        self.config = config
        
        # Frame storage
        self.frame_queue: Queue = Queue(maxsize=10)
        self.depth_queue: Queue = Queue(maxsize=10)
        self.current_frame: Optional[np.ndarray] = None
        self.current_depth: Optional[np.ndarray] = None
        
        # Threading and control
        self.running = False
        self.capture_thread: Optional[threading.Thread] = None
        self.server: Optional[HTTPServer] = None
        
        # Device state
        self.kinect_available = False
        self.kinect_method: Optional[str] = None
        self.device_handle = None
        self.cap: Optional[cv2.VideoCapture] = None
        
        # Statistics
        self.frame_count = 0
        self.start_time = time.time()
        self.error_message: Optional[str] = None
        
        # Initialize device
        self._detect_and_initialize_device()
    
    def _detect_and_initialize_device(self) -> None:
        """Detect and initialize the best available camera method."""
        self.logger.info("🔍 Detecting camera devices...")
        
        # Method 1: Try freenect Python library
        if FREENECT_AVAILABLE and self.config.kinect.enabled:
            if self._try_freenect_python():
                self.kinect_method = 'freenect'
                self.kinect_available = True
                self.logger.info("✅ Kinect detected using freenect Python library")
                return
        
        # Method 2: Try freenect system library
        if self.config.kinect.enabled:
            if self._try_freenect_system():
                self.kinect_method = 'freenect_system'
                self.kinect_available = True
                self.logger.info("✅ Kinect detected using freenect system library")
                return
        
        # Method 3: Try OpenCV (fallback)
        if self.config.kinect.fallback_to_opencv:
            if self._try_opencv():
                self.kinect_method = 'opencv'
                self.kinect_available = True
                self.logger.info("✅ Camera detected using OpenCV")
                return
        
        # No camera found
        self.kinect_available = False
        self.kinect_method = None
        self.error_message = "No camera device detected"
        self.logger.error("❌ No camera device detected")
    
    def _try_freenect_python(self) -> bool:
        """Try to initialize Kinect using freenect Python library."""
        try:
            ctx = freenect.init()
            if not ctx:
                return False
            
            num_devices = freenect.num_devices(ctx)
            if num_devices == 0:
                freenect.shutdown(ctx)
                return False
            
            self.device_handle = freenect.open_device(ctx, 0)
            if not self.device_handle:
                freenect.shutdown(ctx)
                return False
            
            # Set video and depth modes
            freenect.set_video_mode(
                self.device_handle, 
                freenect.find_video_mode(freenect.RESOLUTION_MEDIUM, freenect.VIDEO_RGB)
            )
            freenect.set_depth_mode(
                self.device_handle, 
                freenect.find_depth_mode(freenect.RESOLUTION_MEDIUM, freenect.DEPTH_11BIT)
            )
            
            return True
        except Exception as e:
            self.logger.warning(f"⚠️ freenect Python library failed: {e}")
            return False
    
    def _try_freenect_system(self) -> bool:
        """Try to initialize Kinect using freenect system library."""
        try:
            import ctypes
            from ctypes import cdll, c_int, c_void_p, POINTER
            
            # Try to load libfreenect
            freenect_lib = cdll.LoadLibrary('/usr/local/lib/libfreenect.so')
            
            # Define function signatures
            freenect_lib.freenect_init.argtypes = [POINTER(c_void_p), c_void_p]
            freenect_lib.freenect_init.restype = c_int
            freenect_lib.freenect_num_devices.argtypes = [c_void_p]
            freenect_lib.freenect_num_devices.restype = c_int
            
            # Initialize context
            ctx = c_void_p()
            result = freenect_lib.freenect_init(ctypes.byref(ctx), None)
            if result < 0:
                return False
            
            # Check for devices
            num_devices = freenect_lib.freenect_num_devices(ctx)
            if num_devices == 0:
                return False
            
            self.device_handle = ctx
            return True
        except Exception as e:
            self.logger.warning(f"⚠️ freenect system library failed: {e}")
            return False
    
    def _try_opencv(self) -> bool:
        """Try to initialize camera using OpenCV."""
        try:
            # Try different camera indices
            for camera_idx in [self.config.camera.index, 1, 2, 3, 4, 5]:
                cap = cv2.VideoCapture(camera_idx)
                if cap.isOpened():
                    ret, test_frame = cap.read()
                    if ret and test_frame is not None:
                        self.cap = cap
                        self.config.camera.index = camera_idx
                        
                        # Set camera properties
                        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.config.camera.width)
                        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config.camera.height)
                        self.cap.set(cv2.CAP_PROP_FPS, self.config.camera.fps)
                        
                        return True
                    else:
                        cap.release()
                else:
                    cap.release()
            return False
        except Exception as e:
            self.logger.warning(f"⚠️ OpenCV camera detection failed: {e}")
            return False
    
    def _create_status_frame(self) -> np.ndarray:
        """Create a status frame showing system information."""
        frame = np.zeros((self.config.camera.height, self.config.camera.width, 3), dtype=np.uint8)
        
        if self.kinect_available:
            frame[:] = (0, 50, 0)  # Dark green background
            status_text = f"KINECT READY - {self.kinect_method.upper()}"
            color = (0, 255, 0)
        else:
            frame[:] = (50, 0, 0)  # Dark red background
            status_text = "KINECT NOT AVAILABLE"
            color = (255, 255, 255)
        
        # Add main status text
        cv2.putText(frame, status_text, (120, 200), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1.0, color, 2)
        
        # Add method information
        if self.kinect_method:
            cv2.putText(frame, f"Method: {self.kinect_method}", (200, 250), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 2)
        
        # Add frame counter
        cv2.putText(frame, f"Frame: {self.frame_count}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Add timestamp
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        cv2.putText(frame, timestamp, (10, self.config.camera.height - 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Add error message if any
        if self.error_message:
            cv2.putText(frame, self.error_message[:50], (10, self.config.camera.height - 60), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 100, 100), 1)
        
        return frame
    
    def _capture_frames(self) -> None:
        """Continuously capture frames from the camera."""
        self.logger.info("🎥 Starting frame capture thread")
        
        while self.running:
            try:
                if self.kinect_method in ['freenect', 'freenect_system']:
                    self._capture_freenect_frames()
                elif self.kinect_method == 'opencv':
                    self._capture_opencv_frames()
                else:
                    # No camera available, show status frame
                    frame = self._create_status_frame()
                    self._add_frame_to_queue(frame)
                
                # Print status every 100 frames
                if self.frame_count % 100 == 0:
                    elapsed = time.time() - self.start_time
                    fps = self.frame_count / (elapsed + 0.001)
                    status = f"Camera: {self.kinect_method or 'None'}"
                    self.logger.info(f"Generated {self.frame_count} frames (FPS: {fps:.1f}) - {status}")
                
                time.sleep(1.0 / self.config.camera.fps)
                
            except Exception as e:
                self.logger.error(f"Error in capture loop: {e}")
                time.sleep(1)
    
    def _capture_freenect_frames(self) -> None:
        """Capture frames using freenect."""
        try:
            if self.device_handle and FREENECT_AVAILABLE:
                # Process freenect events
                freenect.process_events(self.device_handle)
                
                # Get RGB frame
                rgb_data = freenect.sync_get_video()[0]
                if rgb_data is not None:
                    frame = rgb_data.reshape((self.config.camera.height, self.config.camera.width, 3))
                    self._add_frame_to_queue(frame)
                
                # Get depth frame
                if self.config.kinect.depth_enabled:
                    depth_data = freenect.sync_get_depth()[0]
                    if depth_data is not None:
                        self._add_depth_to_queue(depth_data)
        except Exception as e:
            self.logger.error(f"Error capturing freenect frames: {e}")
    
    def _capture_opencv_frames(self) -> None:
        """Capture frames using OpenCV."""
        try:
            if self.cap and self.cap.isOpened():
                ret, frame = self.cap.read()
                if ret and frame is not None:
                    self._add_frame_to_queue(frame)
                else:
                    self.logger.warning("Warning: Failed to read frame from OpenCV camera")
        except Exception as e:
            self.logger.error(f"Error capturing OpenCV frames: {e}")
    
    def _add_frame_to_queue(self, frame: np.ndarray) -> None:
        """Add frame to queue with backpressure handling."""
        try:
            if not self.frame_queue.full():
                self.frame_queue.put(frame, timeout=0.1)
                self.current_frame = frame
                self.frame_count += 1
            else:
                # Queue is full, drop oldest frame
                try:
                    self.frame_queue.get_nowait()
                    self.frame_queue.put(frame, timeout=0.1)
                    self.current_frame = frame
                    self.frame_count += 1
                except Empty:
                    pass
        except Exception as e:
            self.logger.error(f"Error adding frame to queue: {e}")
    
    def _add_depth_to_queue(self, depth: np.ndarray) -> None:
        """Add depth frame to queue with backpressure handling."""
        try:
            if not self.depth_queue.full():
                self.depth_queue.put(depth, timeout=0.1)
                self.current_depth = depth
            else:
                # Queue is full, drop oldest frame
                try:
                    self.depth_queue.get_nowait()
                    self.depth_queue.put(depth, timeout=0.1)
                    self.current_depth = depth
                except Empty:
                    pass
        except Exception as e:
            self.logger.error(f"Error adding depth to queue: {e}")
    
    def get_frame(self) -> Optional[np.ndarray]:
        """Get the latest frame."""
        return self.current_frame.copy() if self.current_frame is not None else None
    
    def get_depth_frame(self) -> Optional[np.ndarray]:
        """Get the latest depth frame."""
        return self.current_depth.copy() if self.current_depth is not None else None
    
    def start(self) -> bool:
        """Start the streaming server."""
        self.logger.info("🚀 Starting Kinect streaming server...")
        self.logger.info(f"Host: {self.config.network.host}")
        self.logger.info(f"Port: {self.config.network.port}")
        
        if self.kinect_available:
            self.logger.info(f"✅ Camera detected using: {self.kinect_method}")
        else:
            self.logger.warning("❌ No camera detected - showing status frame")
        
        self.running = True
        
        # Start frame capture thread
        self.capture_thread = threading.Thread(target=self._capture_frames, daemon=True)
        self.capture_thread.start()
        
        # Start HTTP server
        handler = lambda *args: KinectHTTPHandler(self, *args)
        
        try:
            self.server = HTTPServer((self.config.network.host, self.config.network.port), handler)
            self.logger.info(f"✅ Streaming server started on http://{self.config.network.host}:{self.config.network.port}")
            self.logger.info("Available endpoints:")
            self.logger.info("  / - Camera viewer")
            self.logger.info("  /stream - Raw video stream")
            self.logger.info("  /depth - Depth stream (if available)")
            self.logger.info("  /frame - Single frame as JSON")
            self.logger.info("  /status - Server status")
            self.logger.info("  /diagnostic - Diagnostic information")
            
            self.server.serve_forever()
            return True
        except OSError as e:
            if e.errno == 98:  # Address already in use
                self.logger.error(f"❌ Port {self.config.network.port} is already in use")
                self.logger.error("Try a different port or kill the existing process")
            else:
                self.logger.error(f"❌ Server error: {e}")
            return False
        except KeyboardInterrupt:
            self.logger.info("\nShutting down server...")
            self.stop()
            return True
    
    def stop(self) -> None:
        """Stop the streaming server and cleanup resources."""
        self.logger.info("🛑 Stopping streaming server...")
        self.running = False
        
        # Stop HTTP server
        if self.server:
            self.server.shutdown()
            self.server = None
        
        # Wait for capture thread to finish
        if self.capture_thread and self.capture_thread.is_alive():
            self.capture_thread.join(timeout=5.0)
        
        # Cleanup camera resources
        if self.cap:
            self.cap.release()
            self.cap = None
        
        if self.device_handle and FREENECT_AVAILABLE:
            try:
                freenect.shutdown(self.device_handle)
            except:
                pass
            self.device_handle = None
        
        cv2.destroyAllWindows()
        self.logger.info("✅ Server stopped and resources cleaned up")


class KinectHTTPHandler(BaseHTTPRequestHandler):
    """HTTP request handler for Kinect streaming endpoints."""
    
    def __init__(self, streamer: KinectStreamer, *args, **kwargs):
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
        elif self.path == '/frame':
            self._serve_frame()
        elif self.path == '/status':
            self._serve_status()
        elif self.path == '/diagnostic':
            self._serve_diagnostic()
        else:
            self.send_error(404)
    
    def _serve_html(self):
        """Serve the camera viewer HTML page."""
        html = self._get_html_content()
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())
    
    def _serve_stream(self):
        """Serve the video stream."""
        frame = self.streamer.get_frame()
        if frame is None:
            self.send_error(503, "Stream not available")
            return
        
        # Encode frame as JPEG
        _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, self.streamer.config.camera.jpeg_quality])
        
        self.send_response(200)
        self.send_header('Content-type', 'image/jpeg')
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        self.end_headers()
        self.wfile.write(buffer.tobytes())
    
    def _serve_depth_stream(self):
        """Serve the depth video stream."""
        depth_frame = self.streamer.get_depth_frame()
        if depth_frame is None:
            # Create a placeholder depth frame
            placeholder = np.zeros((self.streamer.config.camera.height, self.streamer.config.camera.width, 3), dtype=np.uint8)
            placeholder[:] = (50, 50, 50)  # Dark gray
            cv2.putText(placeholder, "Depth Not Available", (180, 240), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            _, buffer = cv2.imencode('.jpg', placeholder)
        else:
            # Convert depth to colorized image
            depth_colored = cv2.applyColorMap(
                cv2.convertScaleAbs(depth_frame, alpha=255.0/2048.0), 
                cv2.COLORMAP_JET
            )
            _, buffer = cv2.imencode('.jpg', depth_colored, [cv2.IMWRITE_JPEG_QUALITY, self.streamer.config.camera.jpeg_quality])
        
        self.send_response(200)
        self.send_header('Content-type', 'image/jpeg')
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        self.end_headers()
        self.wfile.write(buffer.tobytes())
    
    def _serve_frame(self):
        """Serve a single frame as JSON."""
        frame = self.streamer.get_frame()
        depth_frame = self.streamer.get_depth_frame()
        
        response = {
            'timestamp': time.time(),
            'rgb_available': frame is not None,
            'depth_available': depth_frame is not None,
            'kinect_available': self.streamer.kinect_available,
            'kinect_method': self.streamer.kinect_method
        }
        
        if frame is not None:
            _, buffer = cv2.imencode('.jpg', frame)
            response['rgb_data'] = base64.b64encode(buffer).decode('utf-8')
            response['rgb_width'] = frame.shape[1]
            response['rgb_height'] = frame.shape[0]
        
        if depth_frame is not None:
            _, buffer = cv2.imencode('.jpg', depth_frame)
            response['depth_data'] = base64.b64encode(buffer).decode('utf-8')
            response['depth_width'] = depth_frame.shape[1]
            response['depth_height'] = depth_frame.shape[0]
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())
    
    def _serve_status(self):
        """Serve server status."""
        elapsed = time.time() - self.streamer.start_time
        fps = self.streamer.frame_count / (elapsed + 0.001)
        
        # Check if we have real camera data
        frame = self.streamer.get_frame()
        has_real_camera = frame is not None and self.streamer.kinect_available
        
        status = {
            'running': self.streamer.running,
            'frame_count': self.streamer.frame_count,
            'fps': fps,
            'elapsed_time': elapsed,
            'kinect_available': self.streamer.kinect_available,
            'kinect_method': self.streamer.kinect_method,
            'error_message': self.streamer.error_message,
            'timestamp': time.time(),
            'camera_available': has_real_camera,
            'frame_available': has_real_camera
        }
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(status).encode())
    
    def _serve_diagnostic(self):
        """Serve diagnostic information."""
        elapsed = time.time() - self.streamer.start_time
        fps = self.streamer.frame_count / (elapsed + 0.001)
        
        diagnostic = {
            'stream_type': 'pi_kinect',
            'frame_count': self.streamer.frame_count,
            'fps': fps,
            'elapsed_time': elapsed,
            'server_running': self.streamer.running,
            'kinect_available': self.streamer.kinect_available,
            'kinect_method': self.streamer.kinect_method,
            'freenect_python_available': FREENECT_AVAILABLE,
            'error_message': self.streamer.error_message,
            'timestamp': time.time(),
            'note': 'Pi-Kinect streamer with automatic method detection'
        }
        
        # Check for available video devices
        import glob
        video_devices = glob.glob('/dev/video*')
        diagnostic['available_video_devices'] = video_devices
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(diagnostic, indent=2).encode())
    
    def _get_html_content(self) -> str:
        """Get the HTML content for the camera viewer."""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Pi-Kinect Stream</title>
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
                .controls {
                    margin: 20px 0;
                }
                button {
                    background: #007bff;
                    color: white;
                    border: none;
                    padding: 10px 20px;
                    margin: 5px;
                    border-radius: 5px;
                    cursor: pointer;
                }
                button:hover { background: #0056b3; }
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
                <h1>Pi-Kinect Camera Stream</h1>
                <div class="info">
                    <strong>🎯 Pi-Kinect Streamer:</strong> 
                    Automatically detects and uses the best available camera method.
                </div>
                <div class="status" id="status">Connecting...</div>
                
                <div class="streams">
                    <div class="stream-container">
                        <h3>RGB Camera</h3>
                        <img id="video" src="/stream" alt="RGB Feed">
                    </div>
                    <div class="stream-container">
                        <h3>Depth Camera</h3>
                        <img id="depth" src="/depth" alt="Depth Feed">
                    </div>
                </div>
                
                <div class="controls">
                    <button onclick="refreshStreams()">Refresh</button>
                    <button onclick="checkStatus()">Check Status</button>
                    <button onclick="captureFrame()">Capture Frame</button>
                    <button onclick="toggleFullscreen()">Fullscreen</button>
                </div>
            </div>
            
            <script>
                let videoImg = document.getElementById('video');
                let depthImg = document.getElementById('depth');
                let status = document.getElementById('status');
                let isStreaming = false;
                
                function updateStatus(message, isError = false) {
                    status.textContent = message;
                    status.style.color = isError ? '#dc3545' : '#28a745';
                }
                
                function refreshStreams() {
                    videoImg.src = '/stream?' + new Date().getTime();
                    depthImg.src = '/depth?' + new Date().getTime();
                    updateStatus('Streams refreshed');
                }
                
                function checkStatus() {
                    fetch('/status')
                        .then(response => response.json())
                        .then(data => {
                            let statusText = `Running: ${data.running}, Frames: ${data.frame_count}, FPS: ${data.fps.toFixed(1)}, Camera: ${data.kinect_available ? data.kinect_method : 'Not Available'}`;
                            updateStatus(statusText);
                        })
                        .catch(error => {
                            updateStatus('Status check failed: ' + error, true);
                        });
                }
                
                function captureFrame() {
                    const link = document.createElement('a');
                    link.download = 'kinect_frame_' + new Date().getTime() + '.jpg';
                    link.href = videoImg.src;
                    link.click();
                }
                
                function toggleFullscreen() {
                    if (!document.fullscreenElement) {
                        document.documentElement.requestFullscreen().catch(err => {
                            console.log('Error attempting to enable fullscreen:', err);
                        });
                    } else {
                        document.exitFullscreen();
                    }
                }
                
                // Handle image load events
                function onImageLoad() {
                    if (!isStreaming) {
                        updateStatus('Camera streams connected successfully');
                        isStreaming = true;
                    }
                }
                
                function onImageError() {
                    updateStatus('Stream connection failed', true);
                    isStreaming = false;
                }
                
                videoImg.onload = onImageLoad;
                videoImg.onerror = onImageError;
                depthImg.onload = onImageLoad;
                depthImg.onerror = onImageError;
                
                // Auto-refresh every 30 seconds
                setInterval(refreshStreams, 30000);
            </script>
        </body>
        </html>
        """
    
    def log_message(self, format, *args):
        """Suppress default logging."""
        pass
