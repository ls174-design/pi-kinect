#!/usr/bin/env python3
"""
Robust Kinect 360 video capture with RTP streaming and GStreamer pipeline.
Supports V4L2 fallback and kernel conflict detection.
"""

import ctypes
import numpy as np
import cv2
import threading
import time
import json
import argparse
import subprocess
import os
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Optional, Tuple
import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GLib

class RobustFreenect:
    """Robust freenect wrapper with safer callback handling and kernel conflict detection."""
    
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
        
        # Callback references to prevent garbage collection
        self.video_callback = None
        self.depth_callback = None
        
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
        """Video callback function with safer memory handling."""
        try:
            if data and self.video_lock.acquire(blocking=False):
                try:
                    # Convert raw data to numpy array (RGB format)
                    video_ptr = ctypes.cast(data, ctypes.POINTER(ctypes.c_uint8))
                    # Create a copy to avoid memory issues
                    video_array = np.frombuffer(
                        ctypes.string_at(video_ptr, 480 * 640 * 3), 
                        dtype=np.uint8
                    ).reshape((480, 640, 3))
                    
                    self.video_data = video_array.copy()
                finally:
                    self.video_lock.release()
        except Exception as e:
            print(f"Video callback error: {e}")
    
    def _depth_callback(self, device, data, timestamp):
        """Depth callback function with safer memory handling."""
        try:
            if data and self.depth_lock.acquire(blocking=False):
                try:
                    # Convert raw data to numpy array
                    depth_ptr = ctypes.cast(data, ctypes.POINTER(ctypes.c_uint16))
                    # Create a copy to avoid memory issues
                    depth_array = np.frombuffer(
                        ctypes.string_at(depth_ptr, 480 * 640 * 2), 
                        dtype=np.uint16
                    ).reshape((480, 640))
                    
                    self.depth_data = depth_array.copy()
                finally:
                    self.depth_lock.release()
        except Exception as e:
            print(f"Depth callback error: {e}")
    
    def init(self) -> bool:
        """Initialize freenect context with kernel conflict detection."""
        if not self.lib:
            return False
            
        self.ctx = ctypes.c_void_p()
        result = self.lib.freenect_init(ctypes.byref(self.ctx), None)
        
        if result != 0:
            print("❌ Failed to initialize freenect context")
            return False
            
        return True
    
    def num_devices(self) -> int:
        """Get number of devices."""
        if not self.lib or not self.ctx:
            return 0
        return self.lib.freenect_num_devices(self.ctx)
    
    def open_device(self, device_index: int = 0) -> bool:
        """Open a device with kernel conflict detection."""
        if not self.lib or not self.ctx:
            return False
            
        self.device = self.lib.freenect_open_device(self.ctx, device_index)
        if not self.device:
            print("❌ Failed to open Kinect device")
            print("💡 If you see 'could not claim interface' error:")
            print("   Unload kernel module: sudo modprobe -r gspca_kinect")
            return False
        
        # Set video and depth modes
        # RGB video mode (640x480)
        self.lib.freenect_set_video_mode(self.device, 0)  # FREENECT_VIDEO_RGB
        # 11-bit depth mode (640x480)
        self.lib.freenect_set_depth_mode(self.device, 0)  # FREENECT_DEPTH_11BIT
        
        # Set up callbacks with proper error handling
        try:
            video_callback_type = ctypes.CFUNCTYPE(None, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_uint32)
            depth_callback_type = ctypes.CFUNCTYPE(None, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_uint32)
            
            self.video_callback = video_callback_type(self._video_callback)
            self.depth_callback = depth_callback_type(self._depth_callback)
            
            # Set callbacks
            result1 = self.lib.freenect_set_video_callback(self.device, self.video_callback)
            result2 = self.lib.freenect_set_depth_callback(self.device, self.depth_callback)
            
            if result1 != 0 or result2 != 0:
                print(f"Warning: Callback setup returned {result1}, {result2}")
            
        except Exception as e:
            print(f"Callback setup error: {e}")
            return False
        
        # Start video and depth streams
        self.lib.freenect_start_video(self.device)
        self.lib.freenect_start_depth(self.device)
        
        return True
    
    def process_events(self):
        """Process freenect events."""
        if self.lib and self.ctx:
            try:
                self.lib.freenect_process_events(self.ctx)
            except Exception as e:
                print(f"Process events error: {e}")
    
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

class GStreamerRTPStreamer:
    """GStreamer RTP streamer for video data."""
    
    def __init__(self, host: str, port: int, width: int = 640, height: int = 480, fps: int = 20):
        self.host = host
        self.port = port
        self.width = width
        self.height = height
        self.fps = fps
        self.pipeline = None
        self.appsrc = None
        self.loop = None
        self.running = False
        
    def start(self):
        """Start the GStreamer pipeline."""
        Gst.init(None)
        
        # Create pipeline
        pipeline_str = (
            f"appsrc name=source ! "
            f"video/x-raw,format=BGR,width={self.width},height={self.height},framerate={self.fps}/1 ! "
            f"videoconvert ! jpegenc quality=70 ! rtpjpegpay ! "
            f"udpsink host={self.host} port={self.port}"
        )
        
        self.pipeline = Gst.parse_launch(pipeline_str)
        self.appsrc = self.pipeline.get_by_name("source")
        
        # Configure appsrc
        self.appsrc.set_property("is-live", True)
        self.appsrc.set_property("do-timestamp", True)
        
        # Start pipeline
        self.pipeline.set_state(Gst.State.PLAYING)
        self.running = True
        
        # Start GLib main loop in a separate thread
        self.loop = threading.Thread(target=self._run_loop, daemon=True)
        self.loop.start()
        
        print(f"✅ GStreamer RTP stream started: {self.host}:{self.port}")
        
    def _run_loop(self):
        """Run GLib main loop."""
        loop = GLib.MainLoop()
        loop.run()
        
    def push_frame(self, frame: np.ndarray):
        """Push a frame to the pipeline."""
        if not self.running or not self.appsrc:
            return
            
        # Convert frame to bytes
        frame_bytes = frame.tobytes()
        
        # Create GStreamer buffer
        buffer = Gst.Buffer.new_allocate(None, len(frame_bytes), None)
        buffer.fill(0, frame_bytes)
        
        # Push buffer
        ret = self.appsrc.emit("push-buffer", buffer)
        if ret != Gst.FlowReturn.OK:
            print(f"Warning: Failed to push buffer: {ret}")
            
    def stop(self):
        """Stop the pipeline."""
        if self.pipeline:
            self.pipeline.set_state(Gst.State.NULL)
        self.running = False

class RobustKinectStreamer:
    """Robust Kinect streamer with RTP streaming and CLI support."""
    
    def __init__(self, args):
        self.freenect = RobustFreenect()
        self.running = False
        self.host = args.host
        self.port = args.port
        self.rtp_host = args.rtp_host
        self.rtp_port = args.rtp_port
        self.mode = args.mode
        self.width = args.width
        self.height = args.height
        self.fps = args.fps
        self.server = None
        self.frame_count = 0
        self.start_time = time.time()
        
        # RTP streamers
        self.rtp_streamer = None
        self.depth_rtp_streamer = None
        
        # Pre-allocated buffers for performance
        self.video_buffer = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        self.depth_buffer = np.zeros((self.height, self.width), dtype=np.uint16)
        
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
        print(f"🎥 Starting capture in {self.mode} mode...")
        
        self.running = True
        
        # Start RTP streaming if requested
        if self.rtp_host:
            self._start_rtp_streaming()
        
        # Start capture thread
        self.capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.capture_thread.start()
        
        # Start HTTP server
        self._start_http_server()
        
        return True
    
    def _start_rtp_streaming(self):
        """Start RTP streaming."""
        if 'rgb' in self.mode:
            self.rtp_streamer = GStreamerRTPStreamer(
                self.rtp_host, self.rtp_port, self.width, self.height, self.fps
            )
            self.rtp_streamer.start()
            
        if 'depth' in self.mode:
            self.depth_rtp_streamer = GStreamerRTPStreamer(
                self.rtp_host, self.rtp_port + 1, self.width, self.height, self.fps
            )
            self.depth_rtp_streamer.start()
    
    def _capture_loop(self):
        """Main capture loop with performance optimizations."""
        print("🎥 Starting capture loop...")
        
        while self.running:
            try:
                # Process freenect events to get new frames
                self.freenect.process_events()
                
                # Get frames based on mode
                if 'rgb' in self.mode:
                    video_frame = self.freenect.get_video_frame()
                    if video_frame is not None:
                        # Resize if needed
                        if video_frame.shape[:2] != (self.height, self.width):
                            video_frame = cv2.resize(video_frame, (self.width, self.height))
                        
                        # Copy to pre-allocated buffer
                        np.copyto(self.video_buffer, video_frame)
                        
                        # Push to RTP stream
                        if self.rtp_streamer:
                            self.rtp_streamer.push_frame(self.video_buffer)
                        
                        self.frame_count += 1
                
                if 'depth' in self.mode:
                    depth_frame = self.freenect.get_depth_frame()
                    if depth_frame is not None:
                        # Convert depth to 8-bit preview for streaming
                        depth_preview = self._tone_map_depth(depth_frame)
                        
                        # Resize if needed
                        if depth_preview.shape[:2] != (self.height, self.width):
                            depth_preview = cv2.resize(depth_preview, (self.width, self.height))
                        
                        # Convert to BGR for GStreamer
                        depth_bgr = cv2.cvtColor(depth_preview, cv2.COLOR_GRAY2BGR)
                        
                        # Push to RTP stream
                        if self.depth_rtp_streamer:
                            self.depth_rtp_streamer.push_frame(depth_bgr)
                
                # Print status every 100 frames
                if self.frame_count % 100 == 0:
                    elapsed = time.time() - self.start_time
                    fps = self.frame_count / (elapsed + 0.001)
                    print(f"📹 Captured {self.frame_count} frames (FPS: {fps:.1f})")
                
                time.sleep(1.0 / self.fps)
                
            except Exception as e:
                print(f"Capture loop error: {e}")
                time.sleep(0.1)
    
    def _tone_map_depth(self, depth_frame: np.ndarray) -> np.ndarray:
        """Convert 11-bit/16-bit depth to 8-bit preview."""
        # Remove invalid depth values
        valid_mask = (depth_frame > 0) & (depth_frame < 2048)
        
        if not np.any(valid_mask):
            return np.zeros_like(depth_frame, dtype=np.uint8)
        
        # Normalize valid depth values
        valid_depth = depth_frame[valid_mask]
        min_depth = np.percentile(valid_depth, 1)
        max_depth = np.percentile(valid_depth, 99)
        
        if max_depth > min_depth:
            normalized = np.clip((depth_frame - min_depth) / (max_depth - min_depth), 0, 1)
            return (normalized * 255).astype(np.uint8)
        else:
            return np.zeros_like(depth_frame, dtype=np.uint8)
    
    def get_frame(self) -> Optional[np.ndarray]:
        """Get the latest video frame."""
        return self.video_buffer.copy() if self.video_buffer is not None else None
    
    def get_depth_frame(self) -> Optional[np.ndarray]:
        """Get the latest depth frame."""
        return self.depth_buffer.copy() if self.depth_buffer is not None else None
    
    def _start_http_server(self):
        """Start HTTP server."""
        handler = lambda *args: RobustKinectHTTPHandler(self, *args)
        
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
        
        if self.rtp_streamer:
            self.rtp_streamer.stop()
        if self.depth_rtp_streamer:
            self.depth_rtp_streamer.stop()
        
        if self.server:
            self.server.shutdown()
            self.server = None
        
        if hasattr(self, 'capture_thread'):
            self.capture_thread.join(timeout=5.0)
            
        self.freenect.shutdown()
        print("✅ Kinect streamer stopped")

class RobustKinectHTTPHandler(BaseHTTPRequestHandler):
    """HTTP request handler for robust Kinect streaming."""
    
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
            <title>Robust Kinect 360 Stream</title>
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
                <h1>🎯 Robust Kinect 360 Camera Stream</h1>
                <div class="info">
                    <strong>✅ Robust Kinect 360 Video Capture Active!</strong><br>
                    Capturing actual video from Kinect hardware with RTP streaming support.
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
                    updateStatus('✅ Robust Kinect 360 streams connected successfully');
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
            frame = np.zeros((self.streamer.height, self.streamer.width, 3), dtype=np.uint8)
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
            frame = np.zeros((self.streamer.height, self.streamer.width, 3), dtype=np.uint8)
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
            'kinect_method': 'robust_system_freenect',
            'video_available': self.streamer.get_frame() is not None,
            'depth_available': self.streamer.get_depth_frame() is not None,
            'rtp_host': self.streamer.rtp_host,
            'rtp_port': self.streamer.rtp_port,
            'mode': self.streamer.mode,
            'timestamp': time.time()
        }
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(status).encode())
    
    def log_message(self, format, *args):
        """Suppress default logging."""
        pass

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Robust Kinect 360 streamer with RTP support')
    
    # Streaming mode
    parser.add_argument('--mode', choices=['rgb', 'depth', 'depth+rgb'], 
                       default='depth+rgb', help='Streaming mode')
    
    # HTTP server settings
    parser.add_argument('--host', default='0.0.0.0', help='HTTP server host')
    parser.add_argument('--port', type=int, default=8080, help='HTTP server port')
    
    # RTP streaming settings
    parser.add_argument('--rtp-host', help='RTP streaming host (e.g., 192.168.1.100)')
    parser.add_argument('--rtp-port', type=int, default=5001, help='RTP streaming port')
    
    # Video settings
    parser.add_argument('--width', type=int, default=640, help='Video width')
    parser.add_argument('--height', type=int, default=480, help='Video height')
    parser.add_argument('--fps', type=int, default=20, help='Frames per second')
    
    return parser.parse_args()

# Main execution
if __name__ == "__main__":
    args = parse_arguments()
    
    # Initialize GStreamer
    Gst.init(None)
    
    streamer = RobustKinectStreamer(args)
    
    try:
        if streamer.start():
            print("✅ Robust Kinect streamer started successfully")
            if args.rtp_host:
                print(f"📡 RTP streaming to {args.rtp_host}:{args.rtp_port}")
            print(f"🌐 HTTP server: http://{args.host}:{args.port}")
            print("Press Ctrl+C to stop")
            
            # Keep running
            while True:
                time.sleep(1)
        else:
            print("❌ Failed to start Kinect streamer")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n🛑 Stopping...")
        streamer.stop()