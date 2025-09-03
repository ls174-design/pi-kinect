#!/usr/bin/env python3
"""
Unified Kinect Camera Streamer
Combines the best features from all implementations with proper error handling
"""

import cv2
import numpy as np
import threading
import time
import base64
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
import sys
import os
import ctypes
from ctypes import cdll, c_int, c_void_p, c_char_p, POINTER, Structure, c_uint32, c_uint16, c_uint8

# Try to import freenect for advanced Kinect support
try:
    import freenect
    FREENECT_AVAILABLE = True
    print("✅ freenect Python library available")
except ImportError:
    FREENECT_AVAILABLE = False
    print("⚠️ freenect Python library not available - using OpenCV fallback")

class UnifiedKinectStreamer:
    def __init__(self, host='0.0.0.0', port=8080, camera_index=0):
        self.host = host
        self.port = port
        self.camera_index = camera_index
        self.frame = None
        self.depth_frame = None
        self.lock = threading.Lock()
        self.running = False
        self.frame_count = 0
        self.start_time = time.time()
        self.error_message = None
        
        # Kinect detection results
        self.kinect_available = False
        self.kinect_method = None  # 'freenect', 'opencv', or None
        self.cap = None
        self.freenect_ctx = None
        self.freenect_device = None
        
        # Try to initialize Kinect
        self.detect_kinect()
    
    def detect_kinect(self):
        """Detect and initialize the best available Kinect method"""
        print("🔍 Detecting Kinect camera...")
        
        # Method 1: Try freenect Python library
        if FREENECT_AVAILABLE:
            if self._try_freenect_python():
                self.kinect_method = 'freenect'
                self.kinect_available = True
                print("✅ Kinect detected using freenect Python library")
                return
        
        # Method 2: Try freenect system library
        if self._try_freenect_system():
            self.kinect_method = 'freenect_system'
            self.kinect_available = True
            print("✅ Kinect detected using freenect system library")
            return
        
        # Method 3: Try OpenCV (fallback)
        if self._try_opencv():
            self.kinect_method = 'opencv'
            self.kinect_available = True
            print("✅ Kinect detected using OpenCV")
            return
        
        # No Kinect found
        self.kinect_available = False
        self.kinect_method = None
        self.error_message = "No Kinect camera detected"
        print("❌ No Kinect camera detected")
    
    def _try_freenect_python(self):
        """Try to initialize Kinect using freenect Python library"""
        try:
            ctx = freenect.init()
            if not ctx:
                return False
            
            num_devices = freenect.num_devices(ctx)
            if num_devices == 0:
                freenect.shutdown(ctx)
                return False
            
            self.freenect_ctx = ctx
            self.freenect_device = freenect.open_device(ctx, 0)
            if not self.freenect_device:
                freenect.shutdown(ctx)
                return False
            
            # Set video and depth modes
            freenect.set_video_mode(self.freenect_device, freenect.find_video_mode(
                freenect.RESOLUTION_MEDIUM, freenect.VIDEO_RGB))
            freenect.set_depth_mode(self.freenect_device, freenect.find_depth_mode(
                freenect.RESOLUTION_MEDIUM, freenect.DEPTH_11BIT))
            
            return True
        except Exception as e:
            print(f"⚠️ freenect Python library failed: {e}")
            return False
    
    def _try_freenect_system(self):
        """Try to initialize Kinect using freenect system library"""
        try:
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
            
            self.freenect_ctx = ctx
            return True
        except Exception as e:
            print(f"⚠️ freenect system library failed: {e}")
            return False
    
    def _try_opencv(self):
        """Try to initialize Kinect using OpenCV"""
        try:
            # Try different camera indices
            for camera_idx in [self.camera_index, 1, 2, 3, 4, 5]:
                cap = cv2.VideoCapture(camera_idx)
                if cap.isOpened():
                    ret, test_frame = cap.read()
                    if ret and test_frame is not None:
                        self.cap = cap
                        self.camera_index = camera_idx
                        # Set camera properties
                        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                        self.cap.set(cv2.CAP_PROP_FPS, 30)
                        return True
                    else:
                        cap.release()
                else:
                    cap.release()
            return False
        except Exception as e:
            print(f"⚠️ OpenCV camera detection failed: {e}")
            return False
    
    def create_status_frame(self):
        """Create a status frame showing system information"""
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
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
        cv2.putText(frame, timestamp, (10, 450), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Add error message if any
        if self.error_message:
            cv2.putText(frame, self.error_message[:50], (10, 400), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 100, 100), 1)
        
        return frame
    
    def capture_frames(self):
        """Continuously capture frames from Kinect"""
        while self.running:
            try:
                if self.kinect_method in ['freenect', 'freenect_system']:
                    self._capture_freenect_frames()
                elif self.kinect_method == 'opencv':
                    self._capture_opencv_frames()
                else:
                    # No Kinect available, show status frame
                    frame = self.create_status_frame()
                    with self.lock:
                        self.frame = frame
                    self.frame_count += 1
                
                # Print status every 100 frames
                if self.frame_count % 100 == 0:
                    elapsed = time.time() - self.start_time
                    fps = self.frame_count / (elapsed + 0.001)
                    status = f"Kinect: {self.kinect_method or 'None'}"
                    print(f"Generated {self.frame_count} frames (FPS: {fps:.1f}) - {status}")
                
                time.sleep(0.033)  # ~30 FPS
                
            except Exception as e:
                print(f"Error in capture loop: {e}")
                time.sleep(1)
    
    def _capture_freenect_frames(self):
        """Capture frames using freenect"""
        try:
            if self.freenect_ctx and self.freenect_device:
                # Process freenect events
                freenect.process_events(self.freenect_ctx)
                
                # Get RGB frame
                rgb_data = freenect.sync_get_video()[0]
                if rgb_data is not None:
                    frame = rgb_data.reshape((480, 640, 3))
                    with self.lock:
                        self.frame = frame
                    self.frame_count += 1
                
                # Get depth frame
                depth_data = freenect.sync_get_depth()[0]
                if depth_data is not None:
                    with self.lock:
                        self.depth_frame = depth_data
        except Exception as e:
            print(f"Error capturing freenect frames: {e}")
    
    def _capture_opencv_frames(self):
        """Capture frames using OpenCV"""
        try:
            if self.cap and self.cap.isOpened():
                ret, frame = self.cap.read()
                if ret and frame is not None:
                    with self.lock:
                        self.frame = frame
                    self.frame_count += 1
                else:
                    print("Warning: Failed to read frame from OpenCV camera")
        except Exception as e:
            print(f"Error capturing OpenCV frames: {e}")
    
    def get_frame(self):
        """Get the latest frame"""
        with self.lock:
            return self.frame.copy() if self.frame is not None else None
    
    def get_depth_frame(self):
        """Get the latest depth frame"""
        with self.lock:
            return self.depth_frame.copy() if self.depth_frame is not None else None
    
    def start(self):
        """Start the unified Kinect streaming server"""
        print("🚀 Starting Unified Kinect Streaming Server...")
        print(f"Host: {self.host}")
        print(f"Port: {self.port}")
        
        if self.kinect_available:
            print(f"✅ Kinect detected using: {self.kinect_method}")
        else:
            print("❌ No Kinect detected - showing status frame")
        
        self.running = True
        
        # Start frame capture thread
        capture_thread = threading.Thread(target=self.capture_frames)
        capture_thread.daemon = True
        capture_thread.start()
        
        # Start HTTP server
        handler = lambda *args: UnifiedHTTPHandler(self, *args)
        
        try:
            server = HTTPServer((self.host, self.port), handler)
            print(f"✅ Streaming server started on http://{self.host}:{self.port}")
            print("Available endpoints:")
            print("  / - Kinect viewer")
            print("  /stream - Raw video stream")
            print("  /depth - Depth stream (if available)")
            print("  /frame - Single frame as JSON")
            print("  /status - Server status")
            print("  /diagnostic - Diagnostic information")
            
            server.serve_forever()
        except OSError as e:
            if e.errno == 98:  # Address already in use
                print(f"❌ Port {self.port} is already in use")
                print("Try a different port or kill the existing process")
            else:
                print(f"❌ Server error: {e}")
            return False
        except KeyboardInterrupt:
            print("\nShutting down server...")
            self.stop()
            server.shutdown()
    
    def stop(self):
        """Stop the streaming and cleanup"""
        self.running = False
        
        if self.cap:
            self.cap.release()
        
        if self.freenect_ctx and FREENECT_AVAILABLE:
            try:
                freenect.shutdown(self.freenect_ctx)
            except:
                pass
        
        cv2.destroyAllWindows()

class UnifiedHTTPHandler(BaseHTTPRequestHandler):
    def __init__(self, streamer, *args, **kwargs):
        self.streamer = streamer
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        if self.path == '/':
            self.serve_html()
        elif self.path == '/stream':
            self.serve_stream()
        elif self.path == '/depth':
            self.serve_depth_stream()
        elif self.path == '/frame':
            self.serve_frame()
        elif self.path == '/status':
            self.serve_status()
        elif self.path == '/diagnostic':
            self.serve_diagnostic()
        else:
            self.send_error(404)
    
    def serve_html(self):
        """Serve the unified Kinect viewer HTML page"""
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Unified Kinect Stream</title>
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
                <h1>Unified Kinect Camera Stream</h1>
                <div class="info">
                    <strong>🎯 Unified Kinect Streamer:</strong> 
                    Automatically detects and uses the best available Kinect method.
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
                            let statusText = `Running: ${data.running}, Frames: ${data.frame_count}, FPS: ${data.fps.toFixed(1)}, Kinect: ${data.kinect_available ? data.kinect_method : 'Not Available'}`;
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
                        updateStatus('Kinect streams connected successfully');
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
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())
    
    def serve_stream(self):
        """Serve the video stream"""
        frame = self.streamer.get_frame()
        if frame is None:
            self.send_error(503, "Stream not available")
            return
        
        # Encode frame as JPEG
        _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
        
        self.send_response(200)
        self.send_header('Content-type', 'image/jpeg')
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        self.end_headers()
        self.wfile.write(buffer.tobytes())
    
    def serve_depth_stream(self):
        """Serve the depth video stream"""
        depth_frame = self.streamer.get_depth_frame()
        if depth_frame is None:
            # Create a placeholder depth frame
            placeholder = np.zeros((480, 640, 3), dtype=np.uint8)
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
            _, buffer = cv2.imencode('.jpg', depth_colored, [cv2.IMWRITE_JPEG_QUALITY, 85])
        
        self.send_response(200)
        self.send_header('Content-type', 'image/jpeg')
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        self.end_headers()
        self.wfile.write(buffer.tobytes())
    
    def serve_frame(self):
        """Serve a single frame as JSON"""
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
    
    def serve_status(self):
        """Serve server status"""
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
            # Add compatibility fields for the viewer
            'camera_available': has_real_camera,
            'frame_available': has_real_camera
        }
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(status).encode())
    
    def serve_diagnostic(self):
        """Serve diagnostic information"""
        elapsed = time.time() - self.streamer.start_time
        fps = self.streamer.frame_count / (elapsed + 0.001)
        
        diagnostic = {
            'stream_type': 'unified_kinect',
            'frame_count': self.streamer.frame_count,
            'fps': fps,
            'elapsed_time': elapsed,
            'server_running': self.streamer.running,
            'kinect_available': self.streamer.kinect_available,
            'kinect_method': self.streamer.kinect_method,
            'freenect_python_available': FREENECT_AVAILABLE,
            'error_message': self.streamer.error_message,
            'timestamp': time.time(),
            'note': 'Unified Kinect streamer with automatic method detection'
        }
        
        # Check for available video devices
        import glob
        video_devices = glob.glob('/dev/video*')
        diagnostic['available_video_devices'] = video_devices
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(diagnostic, indent=2).encode())
    
    def log_message(self, format, *args):
        """Suppress default logging"""
        pass

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Unified Kinect Streaming Server')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to (default: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=8080, help='Port to bind to (default: 8080)')
    parser.add_argument('--camera', type=int, default=0, help='Camera index for OpenCV fallback (default: 0)')
    
    args = parser.parse_args()
    
    print("🎯 Starting Unified Kinect Streaming Server...")
    print(f"Host: {args.host}")
    print(f"Port: {args.port}")
    print(f"Camera index: {args.camera}")
    
    streamer = UnifiedKinectStreamer(args.host, args.port, args.camera)
    
    try:
        if not streamer.start():
            print("❌ Failed to start streaming server")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\nShutting down...")
        streamer.stop()

if __name__ == '__main__':
    main()
