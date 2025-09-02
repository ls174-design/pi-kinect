#!/usr/bin/env python3
"""
Kinect camera streaming server for Raspberry Pi
Uses libfreenect to stream Kinect camera feed over HTTP
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

# Try to import freenect
try:
    import freenect
    FREENECT_AVAILABLE = True
except ImportError:
    FREENECT_AVAILABLE = False
    print("Warning: freenect not available. Install with: pip install freenect")

class KinectStreamer:
    def __init__(self, host='0.0.0.0', port=8080):
        self.host = host
        self.port = port
        self.rgb_frame = None
        self.depth_frame = None
        self.lock = threading.Lock()
        self.running = False
        self.device = None
        self.ctx = None
        
    def start_kinect(self):
        """Initialize Kinect device"""
        if not FREENECT_AVAILABLE:
            print("Error: freenect not available")
            return False
            
        try:
            # Initialize freenect
            self.ctx = freenect.init()
            if not self.ctx:
                print("Error: Could not initialize freenect")
                return False
            
            # Get number of devices
            num_devices = freenect.num_devices(self.ctx)
            if num_devices == 0:
                print("Error: No Kinect devices found")
                freenect.shutdown(self.ctx)
                return False
            
            print(f"Found {num_devices} Kinect device(s)")
            
            # Open first device
            self.device = freenect.open_device(self.ctx, 0)
            if not self.device:
                print("Error: Could not open Kinect device")
                freenect.shutdown(self.ctx)
                return False
            
            # Set video mode
            freenect.set_video_mode(self.device, freenect.find_video_mode(
                freenect.RESOLUTION_MEDIUM, freenect.VIDEO_RGB))
            
            # Set depth mode
            freenect.set_depth_mode(self.device, freenect.find_depth_mode(
                freenect.RESOLUTION_MEDIUM, freenect.DEPTH_11BIT))
            
            print("Kinect device initialized successfully")
            return True
            
        except Exception as e:
            print(f"Error initializing Kinect: {e}")
            return False
    
    def rgb_callback(self, device, rgb_data, timestamp):
        """Callback for RGB data"""
        with self.lock:
            # Convert RGB data to numpy array
            rgb_array = np.frombuffer(rgb_data, dtype=np.uint8)
            self.rgb_frame = rgb_array.reshape((480, 640, 3))
    
    def depth_callback(self, device, depth_data, timestamp):
        """Callback for depth data"""
        with self.lock:
            # Convert depth data to numpy array
            depth_array = np.frombuffer(depth_data, dtype=np.uint16)
            self.depth_frame = depth_array.reshape((480, 640))
    
    def capture_frames(self):
        """Continuously capture frames from Kinect"""
        while self.running:
            if self.device:
                try:
                    freenect.process_events(self.ctx)
                except Exception as e:
                    print(f"Error processing events: {e}")
            time.sleep(0.033)  # ~30 FPS
    
    def get_rgb_frame(self):
        """Get the latest RGB frame"""
        with self.lock:
            return self.rgb_frame.copy() if self.rgb_frame is not None else None
    
    def get_depth_frame(self):
        """Get the latest depth frame"""
        with self.lock:
            return self.depth_frame.copy() if self.depth_frame is not None else None
    
    def start(self):
        """Start the Kinect streaming server"""
        if not self.start_kinect():
            return False
            
        self.running = True
        
        # Set callbacks
        freenect.set_video_callback(self.device, self.rgb_callback)
        freenect.set_depth_callback(self.device, self.depth_callback)
        
        # Start video and depth streams
        freenect.start_video(self.device)
        freenect.start_depth(self.device)
        
        # Start frame capture thread
        capture_thread = threading.Thread(target=self.capture_frames)
        capture_thread.daemon = True
        capture_thread.start()
        
        # Start HTTP server
        handler = lambda *args: KinectHTTPHandler(self, *args)
        server = HTTPServer((self.host, self.port), handler)
        
        print(f"Kinect streaming server started on http://{self.host}:{self.port}")
        print("Available endpoints:")
        print("  / - Kinect viewer")
        print("  /rgb - RGB stream")
        print("  /depth - Depth stream")
        print("  /frame - Single frame as JSON")
        print("  /status - Server status")
        
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server...")
            self.stop()
            server.shutdown()
    
    def stop(self):
        """Stop the Kinect streaming"""
        self.running = False
        if self.device:
            freenect.stop_video(self.device)
            freenect.stop_depth(self.device)
            freenect.close_device(self.device)
        if self.ctx:
            freenect.shutdown(self.ctx)

class KinectHTTPHandler(BaseHTTPRequestHandler):
    def __init__(self, streamer, *args, **kwargs):
        self.streamer = streamer
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        if self.path == '/':
            self.serve_html()
        elif self.path == '/rgb':
            self.serve_rgb_stream()
        elif self.path == '/depth':
            self.serve_depth_stream()
        elif self.path == '/frame':
            self.serve_frame()
        elif self.path == '/status':
            self.serve_status()
        else:
            self.send_error(404)
    
    def serve_html(self):
        """Serve the Kinect viewer HTML page"""
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Kinect Stream</title>
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
                #rgb, #depth { 
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
                <h1>Raspberry Pi Kinect Stream</h1>
                <div class="status" id="status">Connecting...</div>
                
                <div class="streams">
                    <div class="stream-container">
                        <h3>RGB Camera</h3>
                        <img id="rgb" src="/rgb" alt="RGB Feed">
                    </div>
                    <div class="stream-container">
                        <h3>Depth Camera</h3>
                        <img id="depth" src="/depth" alt="Depth Feed">
                    </div>
                </div>
                
                <div class="controls">
                    <button onclick="refreshStreams()">Refresh</button>
                    <button onclick="captureFrame()">Capture Frame</button>
                    <button onclick="toggleFullscreen()">Fullscreen</button>
                </div>
            </div>
            
            <script>
                let rgbImg = document.getElementById('rgb');
                let depthImg = document.getElementById('depth');
                let status = document.getElementById('status');
                let isStreaming = false;
                
                function updateStatus(message, isError = false) {
                    status.textContent = message;
                    status.style.color = isError ? '#dc3545' : '#28a745';
                }
                
                function refreshStreams() {
                    rgbImg.src = '/rgb?' + new Date().getTime();
                    depthImg.src = '/depth?' + new Date().getTime();
                    updateStatus('Streams refreshed');
                }
                
                function captureFrame() {
                    const link = document.createElement('a');
                    link.download = 'kinect_frame_' + new Date().getTime() + '.jpg';
                    link.href = rgbImg.src;
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
                
                rgbImg.onload = onImageLoad;
                rgbImg.onerror = onImageError;
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
    
    def serve_rgb_stream(self):
        """Serve the RGB video stream"""
        frame = self.streamer.get_rgb_frame()
        if frame is None:
            self.send_error(503, "RGB camera not available")
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
        frame = self.streamer.get_depth_frame()
        if frame is None:
            self.send_error(503, "Depth camera not available")
            return
        
        # Convert depth to colorized image
        depth_colored = cv2.applyColorMap(
            cv2.convertScaleAbs(frame, alpha=255.0/2048.0), 
            cv2.COLORMAP_JET
        )
        
        # Encode frame as JPEG
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
        rgb_frame = self.streamer.get_rgb_frame()
        depth_frame = self.streamer.get_depth_frame()
        
        response = {
            'timestamp': time.time(),
            'rgb_available': rgb_frame is not None,
            'depth_available': depth_frame is not None
        }
        
        if rgb_frame is not None:
            _, buffer = cv2.imencode('.jpg', rgb_frame)
            response['rgb_data'] = base64.b64encode(buffer).decode('utf-8')
            response['rgb_width'] = rgb_frame.shape[1]
            response['rgb_height'] = rgb_frame.shape[0]
        
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
        status = {
            'running': self.streamer.running,
            'kinect_available': self.streamer.device is not None,
            'rgb_available': self.streamer.get_rgb_frame() is not None,
            'depth_available': self.streamer.get_depth_frame() is not None,
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
    
    parser = argparse.ArgumentParser(description='Kinect Streaming Server')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to (default: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=8080, help='Port to bind to (default: 8080)')
    
    args = parser.parse_args()
    
    print("Starting Kinect Streaming Server...")
    print(f"Host: {args.host}")
    print(f"Port: {args.port}")
    
    if not FREENECT_AVAILABLE:
        print("Error: freenect not available. Please install it first.")
        print("On Raspberry Pi: sudo apt-get install python3-freenect")
        print("Or: pip install freenect")
        return 1
    
    streamer = KinectStreamer(args.host, args.port)
    
    try:
        streamer.start()
    except KeyboardInterrupt:
        print("\nShutting down...")
        streamer.stop()
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
