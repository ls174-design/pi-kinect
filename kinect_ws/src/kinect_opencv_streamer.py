#!/usr/bin/env python3
"""
Kinect Camera Streamer using OpenCV
Works with Kinect cameras that are accessible through OpenCV
"""

import cv2
import threading
import time
import base64
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
import sys
import os

class KinectOpenCVStreamer:
    def __init__(self, host='0.0.0.0', port=8080, camera_index=0):
        self.host = host
        self.port = port
        self.camera_index = camera_index
        self.cap = None
        self.frame = None
        self.lock = threading.Lock()
        self.running = False
        self.error_message = None
        
    def start_camera(self):
        """Initialize Kinect camera capture using OpenCV"""
        try:
            print(f"Attempting to open Kinect camera at index {self.camera_index}...")
            
            # Try different camera indices for Kinect
            for camera_idx in [self.camera_index, 1, 2, 3, 4, 5, 6, 7, 8, 9]:
                print(f"Trying camera index {camera_idx}...")
                self.cap = cv2.VideoCapture(camera_idx)
                
                if self.cap.isOpened():
                    # Test if we can read a frame
                    ret, test_frame = self.cap.read()
                    if ret and test_frame is not None:
                        print(f"✅ Kinect camera found at index {camera_idx}")
                        print(f"Frame size: {test_frame.shape}")
                        self.camera_index = camera_idx
                        
                        # Set camera properties for better performance
                        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                        self.cap.set(cv2.CAP_PROP_FPS, 30)
                        
                        self.error_message = None
                        return True
                    else:
                        self.cap.release()
                else:
                    self.cap.release()
            
            self.error_message = "No accessible Kinect camera found"
            print(f"❌ {self.error_message}")
            return False
            
        except Exception as e:
            self.error_message = f"Error initializing Kinect camera: {e}"
            print(f"❌ {self.error_message}")
            return False
    
    def capture_frames(self):
        """Continuously capture frames from Kinect"""
        frame_count = 0
        error_count = 0
        
        while self.running:
            if self.cap and self.cap.isOpened():
                ret, frame = self.cap.read()
                if ret and frame is not None:
                    with self.lock:
                        self.frame = frame
                    frame_count += 1
                    error_count = 0
                    
                    if frame_count % 100 == 0:
                        print(f"Captured {frame_count} frames from Kinect")
                else:
                    error_count += 1
                    if error_count % 10 == 0:
                        print(f"Warning: Failed to read frame from Kinect (error #{error_count})")
                    
                    if error_count > 50:
                        print("Too many errors, attempting to restart camera...")
                        self.restart_camera()
                        error_count = 0
            else:
                print("Kinect camera not available, attempting to restart...")
                self.restart_camera()
                time.sleep(1)
            
            time.sleep(0.033)  # ~30 FPS
    
    def restart_camera(self):
        """Restart the Kinect camera"""
        try:
            if self.cap:
                self.cap.release()
            time.sleep(0.5)
            self.start_camera()
        except Exception as e:
            print(f"Error restarting Kinect camera: {e}")
    
    def get_frame(self):
        """Get the latest frame"""
        with self.lock:
            return self.frame.copy() if self.frame is not None else None
    
    def start(self):
        """Start the Kinect streaming server"""
        print("Starting Kinect OpenCV Streaming Server...")
        
        if not self.start_camera():
            print("❌ Failed to start Kinect camera")
            return False
            
        self.running = True
        
        # Start frame capture thread
        capture_thread = threading.Thread(target=self.capture_frames)
        capture_thread.daemon = True
        capture_thread.start()
        
        # Start HTTP server
        handler = lambda *args: KinectHTTPHandler(self, *args)
        
        try:
            server = HTTPServer((self.host, self.port), handler)
            print(f"✅ Kinect streaming server started on http://{self.host}:{self.port}")
            print("Available endpoints:")
            print("  / - Kinect viewer")
            print("  /stream - Raw video stream")
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
        """Stop the Kinect streaming"""
        self.running = False
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()

class KinectHTTPHandler(BaseHTTPRequestHandler):
    def __init__(self, streamer, *args, **kwargs):
        self.streamer = streamer
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        if self.path == '/':
            self.serve_html()
        elif self.path == '/stream':
            self.serve_stream()
        elif self.path == '/frame':
            self.serve_frame()
        elif self.path == '/status':
            self.serve_status()
        elif self.path == '/diagnostic':
            self.serve_diagnostic()
        else:
            self.send_error(404)
    
    def serve_html(self):
        """Serve the Kinect viewer HTML page"""
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Kinect Camera Stream</title>
            <style>
                body { 
                    font-family: Arial, sans-serif; 
                    text-align: center; 
                    background-color: #f0f0f0;
                    margin: 0;
                    padding: 20px;
                }
                .container {
                    max-width: 800px;
                    margin: 0 auto;
                    background: white;
                    padding: 20px;
                    border-radius: 10px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }
                h1 { color: #333; }
                #video { 
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
                .error { color: #dc3545; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Raspberry Pi Kinect Stream</h1>
                <div class="status" id="status">Connecting...</div>
                <img id="video" src="/stream" alt="Kinect Feed">
                <div class="controls">
                    <button onclick="refreshStream()">Refresh</button>
                    <button onclick="checkStatus()">Check Status</button>
                    <button onclick="captureFrame()">Capture Frame</button>
                </div>
            </div>
            
            <script>
                let streamImg = document.getElementById('video');
                let status = document.getElementById('status');
                let isStreaming = false;
                
                function updateStatus(message, isError = false) {
                    status.textContent = message;
                    status.className = isError ? 'status error' : 'status';
                }
                
                function refreshStream() {
                    streamImg.src = '/stream?' + new Date().getTime();
                    updateStatus('Stream refreshed');
                }
                
                function checkStatus() {
                    fetch('/status')
                        .then(response => response.json())
                        .then(data => {
                            let statusText = `Running: ${data.running}, Camera: ${data.camera_available}, Frame: ${data.frame_available}`;
                            updateStatus(statusText);
                        })
                        .catch(error => {
                            updateStatus('Status check failed: ' + error, true);
                        });
                }
                
                function captureFrame() {
                    const link = document.createElement('a');
                    link.download = 'kinect_frame_' + new Date().getTime() + '.jpg';
                    link.href = streamImg.src;
                    link.click();
                }
                
                // Handle image load events
                streamImg.onload = function() {
                    if (!isStreaming) {
                        updateStatus('Kinect stream connected successfully');
                        isStreaming = true;
                    }
                };
                
                streamImg.onerror = function() {
                    updateStatus('Stream connection failed', true);
                    isStreaming = false;
                };
                
                // Auto-refresh every 30 seconds
                setInterval(refreshStream, 30000);
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
            # Send a placeholder image
            placeholder = self.create_placeholder_image()
            self.send_response(200)
            self.send_header('Content-type', 'image/jpeg')
            self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Expires', '0')
            self.end_headers()
            self.wfile.write(placeholder)
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
    
    def create_placeholder_image(self):
        """Create a placeholder image when camera is not available"""
        import numpy as np
        placeholder = np.zeros((480, 640, 3), dtype=np.uint8)
        placeholder[:] = (50, 50, 50)  # Dark gray
        
        # Add text
        cv2.putText(placeholder, "Kinect Camera Not Available", (120, 200), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv2.putText(placeholder, "Check Kinect connection", (140, 250), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 2)
        
        _, buffer = cv2.imencode('.jpg', placeholder)
        return buffer.tobytes()
    
    def serve_frame(self):
        """Serve a single frame as JSON"""
        frame = self.streamer.get_frame()
        if frame is None:
            self.send_error(503, "Kinect camera not available")
            return
        
        # Encode frame as base64
        _, buffer = cv2.imencode('.jpg', frame)
        frame_base64 = base64.b64encode(buffer).decode('utf-8')
        
        response = {
            'timestamp': time.time(),
            'width': frame.shape[1],
            'height': frame.shape[0],
            'format': 'jpeg',
            'data': frame_base64
        }
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())
    
    def serve_status(self):
        """Serve server status"""
        status = {
            'running': self.streamer.running,
            'camera_available': self.streamer.cap is not None and self.streamer.cap.isOpened(),
            'frame_available': self.streamer.get_frame() is not None,
            'camera_index': self.streamer.camera_index,
            'error_message': self.streamer.error_message,
            'timestamp': time.time()
        }
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(status).encode())
    
    def serve_diagnostic(self):
        """Serve diagnostic information"""
        diagnostic = {
            'camera_index': self.streamer.camera_index,
            'error_message': self.streamer.error_message,
            'camera_opened': self.streamer.cap is not None and self.streamer.cap.isOpened(),
            'frame_available': self.streamer.get_frame() is not None,
            'server_running': self.streamer.running,
            'timestamp': time.time()
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
    
    parser = argparse.ArgumentParser(description='Kinect OpenCV Streaming Server')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to (default: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=8080, help='Port to bind to (default: 8080)')
    parser.add_argument('--camera', type=int, default=0, help='Camera index (default: 0)')
    
    args = parser.parse_args()
    
    print("Starting Kinect OpenCV Streaming Server...")
    print(f"Host: {args.host}")
    print(f"Port: {args.port}")
    print(f"Camera: {args.camera}")
    
    streamer = KinectOpenCVStreamer(args.host, args.port, args.camera)
    
    try:
        if not streamer.start():
            print("❌ Failed to start Kinect streaming server")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\nShutting down...")
        streamer.stop()

if __name__ == '__main__':
    main()
