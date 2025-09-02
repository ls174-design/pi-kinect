#!/usr/bin/env python3
"""
Simple camera streaming server for Raspberry Pi
Streams camera feed over HTTP for remote viewing
"""

import cv2
import socket
import threading
import time
import base64
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
import io
from PIL import Image

class CameraStreamer:
    def __init__(self, host='0.0.0.0', port=8080, camera_index=0):
        self.host = host
        self.port = port
        self.camera_index = camera_index
        self.cap = None
        self.frame = None
        self.lock = threading.Lock()
        self.running = False
        
    def start_camera(self):
        """Initialize camera capture"""
        try:
            self.cap = cv2.VideoCapture(self.camera_index)
            if not self.cap.isOpened():
                print(f"Error: Could not open camera {self.camera_index}")
                return False
                
            # Set camera properties
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.cap.set(cv2.CAP_PROP_FPS, 30)
            
            print(f"Camera {self.camera_index} initialized successfully")
            return True
        except Exception as e:
            print(f"Error initializing camera: {e}")
            return False
    
    def capture_frames(self):
        """Continuously capture frames from camera"""
        while self.running:
            if self.cap and self.cap.isOpened():
                ret, frame = self.cap.read()
                if ret:
                    with self.lock:
                        self.frame = frame
                else:
                    print("Warning: Failed to read frame from camera")
            time.sleep(0.033)  # ~30 FPS
    
    def get_frame(self):
        """Get the latest frame"""
        with self.lock:
            return self.frame.copy() if self.frame is not None else None
    
    def start(self):
        """Start the camera streaming server"""
        if not self.start_camera():
            return False
            
        self.running = True
        
        # Start frame capture thread
        capture_thread = threading.Thread(target=self.capture_frames)
        capture_thread.daemon = True
        capture_thread.start()
        
        # Start HTTP server
        handler = lambda *args: CameraHTTPHandler(self, *args)
        server = HTTPServer((self.host, self.port), handler)
        
        print(f"Camera streaming server started on http://{self.host}:{self.port}")
        print("Available endpoints:")
        print("  / - Camera feed viewer")
        print("  /stream - Raw video stream")
        print("  /frame - Single frame as JSON")
        print("  /status - Server status")
        
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server...")
            self.stop()
            server.shutdown()
    
    def stop(self):
        """Stop the camera streaming"""
        self.running = False
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()

class CameraHTTPHandler(BaseHTTPRequestHandler):
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
        else:
            self.send_error(404)
    
    def serve_html(self):
        """Serve the camera viewer HTML page"""
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Camera Stream</title>
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
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Raspberry Pi Camera Stream</h1>
                <div class="status" id="status">Connecting...</div>
                <img id="video" src="/stream" alt="Camera Feed">
                <div class="controls">
                    <button onclick="refreshStream()">Refresh</button>
                    <button onclick="toggleFullscreen()">Fullscreen</button>
                    <button onclick="captureFrame()">Capture Frame</button>
                </div>
            </div>
            
            <script>
                let streamImg = document.getElementById('video');
                let status = document.getElementById('status');
                let isStreaming = false;
                
                function updateStatus(message, isError = false) {
                    status.textContent = message;
                    status.style.color = isError ? '#dc3545' : '#28a745';
                }
                
                function refreshStream() {
                    streamImg.src = '/stream?' + new Date().getTime();
                    updateStatus('Stream refreshed');
                }
                
                function toggleFullscreen() {
                    if (!document.fullscreenElement) {
                        streamImg.requestFullscreen().catch(err => {
                            console.log('Error attempting to enable fullscreen:', err);
                        });
                    } else {
                        document.exitFullscreen();
                    }
                }
                
                function captureFrame() {
                    const link = document.createElement('a');
                    link.download = 'camera_frame_' + new Date().getTime() + '.jpg';
                    link.href = streamImg.src;
                    link.click();
                }
                
                // Handle image load events
                streamImg.onload = function() {
                    if (!isStreaming) {
                        updateStatus('Stream connected successfully');
                        isStreaming = true;
                    }
                };
                
                streamImg.onerror = function() {
                    updateStatus('Stream connection failed', true);
                    isStreaming = false;
                };
                
                // Auto-refresh every 30 seconds to maintain connection
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
            self.send_error(503, "Camera not available")
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
    
    def serve_frame(self):
        """Serve a single frame as JSON"""
        frame = self.streamer.get_frame()
        if frame is None:
            self.send_error(503, "Camera not available")
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
            'timestamp': time.time()
        }
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(status).encode())
    
    def log_message(self, format, *args):
        """Suppress default logging"""
        pass

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Camera Streaming Server')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to (default: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=8080, help='Port to bind to (default: 8080)')
    parser.add_argument('--camera', type=int, default=0, help='Camera index (default: 0)')
    
    args = parser.parse_args()
    
    print("Starting Camera Streaming Server...")
    print(f"Host: {args.host}")
    print(f"Port: {args.port}")
    print(f"Camera: {args.camera}")
    
    streamer = CameraStreamer(args.host, args.port, args.camera)
    
    try:
        streamer.start()
    except KeyboardInterrupt:
        print("\nShutting down...")
        streamer.stop()

if __name__ == '__main__':
    main()
