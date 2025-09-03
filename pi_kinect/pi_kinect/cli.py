"""
Command-line interface for Pi-Kinect.

Provides CLI commands for device probing, streaming, and viewer functionality.
"""

import argparse
import sys
import signal
from pathlib import Path
from typing import Optional

from .config import Config
from .streamer import KinectStreamer
from .logging_config import setup_logging
from .exceptions import PiKinectError


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Pi-Kinect: Raspberry Pi Kinect streaming solution",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  pi-kinect probe                    # Probe for available devices
  pi-kinect stream                   # Start streaming server
  pi-kinect stream --port 8081       # Start on custom port
  pi-kinect viewer                   # Start GUI viewer
  pi-kinect --config custom.yaml stream  # Use custom config
        """
    )
    
    parser.add_argument(
        "--config", "-c",
        type=str,
        help="Path to configuration file (YAML)"
    )
    parser.add_argument(
        "--debug", "-d",
        action="store_true",
        help="Enable debug mode"
    )
    parser.add_argument(
        "--version", "-v",
        action="version",
        version="pi-kinect 1.0.0"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Probe command
    probe_parser = subparsers.add_parser("probe", help="Probe for available devices")
    probe_parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )
    
    # Stream command
    stream_parser = subparsers.add_parser("stream", help="Start streaming server")
    stream_parser.add_argument(
        "--host",
        type=str,
        help="Host to bind to (default: 0.0.0.0)"
    )
    stream_parser.add_argument(
        "--port", "-p",
        type=int,
        help="Port to bind to (default: 8080)"
    )
    stream_parser.add_argument(
        "--camera", "-c",
        type=int,
        help="Camera index (default: 0)"
    )
    
    # Viewer command
    viewer_parser = subparsers.add_parser("viewer", help="Start GUI viewer")
    viewer_parser.add_argument(
        "--pi-ip",
        type=str,
        help="Raspberry Pi IP address"
    )
    viewer_parser.add_argument(
        "--pi-port",
        type=int,
        help="Raspberry Pi port"
    )
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    try:
        # Load configuration
        config = Config.load(args.config)
        if args.debug:
            config.debug = True
            config.logging.level = "DEBUG"
        
        # Setup logging
        logger = setup_logging(config.logging)
        
        # Handle command
        if args.command == "probe":
            probe_devices(config, args.verbose)
        elif args.command == "stream":
            start_streaming(config, args)
        elif args.command == "viewer":
            start_viewer(config, args)
        else:
            parser.print_help()
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        sys.exit(0)
    except PiKinectError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        if config.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)


def probe_devices(config: Config, verbose: bool = False) -> None:
    """Probe for available camera devices."""
    print("🔍 Probing for available camera devices...")
    
    # Check freenect availability
    try:
        import freenect
        print("✅ freenect Python library available")
        
        if verbose:
            ctx = freenect.init()
            if ctx:
                num_devices = freenect.num_devices(ctx)
                print(f"   Found {num_devices} freenect devices")
                freenect.shutdown(ctx)
            else:
                print("   Failed to initialize freenect context")
    except ImportError:
        print("❌ freenect Python library not available")
    except Exception as e:
        print(f"⚠️ freenect test failed: {e}")
    
    # Check OpenCV cameras
    import cv2
    print("\n📹 Checking OpenCV cameras...")
    
    for i in range(5):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret and frame is not None:
                print(f"✅ Camera {i}: {frame.shape[1]}x{frame.shape[0]}")
                if verbose:
                    print(f"   FPS: {cap.get(cv2.CAP_PROP_FPS)}")
                    print(f"   Backend: {cap.getBackendName()}")
            else:
                print(f"⚠️ Camera {i}: Opened but no frames")
            cap.release()
        else:
            if verbose:
                print(f"❌ Camera {i}: Not available")
    
    # Check system video devices
    import glob
    video_devices = glob.glob('/dev/video*')
    if video_devices:
        print(f"\n📱 System video devices: {', '.join(video_devices)}")
    else:
        print("\n📱 No system video devices found")
    
    print("\n🎯 Device probe complete!")


def start_streaming(config: Config, args: argparse.Namespace) -> None:
    """Start the streaming server."""
    # Override config with command line arguments
    if args.host:
        config.network.host = args.host
    if args.port:
        config.network.port = args.port
    if args.camera is not None:
        config.camera.index = args.camera
    
    # Create and start streamer
    streamer = KinectStreamer(config)
    
    # Setup signal handlers for graceful shutdown
    def signal_handler(signum, frame):
        print(f"\nReceived signal {signum}, shutting down...")
        streamer.stop()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Start streaming
    if not streamer.start():
        sys.exit(1)


def start_viewer(config: Config, args: argparse.Namespace) -> None:
    """Start the GUI viewer."""
    # Override config with command line arguments
    if args.pi_ip:
        config.pi_ip = args.pi_ip
    if args.pi_port:
        config.network.port = args.pi_port
    
    try:
        from .viewer import CameraViewer
        import tkinter as tk
        
        root = tk.Tk()
        app = CameraViewer(root, config)
        
        def on_closing():
            app.stop()
            root.destroy()
        
        root.protocol("WM_DELETE_WINDOW", on_closing)
        root.mainloop()
        
    except ImportError as e:
        print(f"Error: GUI dependencies not available: {e}")
        print("Please install tkinter: sudo apt-get install python3-tk")
        sys.exit(1)


# Convenience functions for direct script execution
def probe_devices_cli() -> None:
    """CLI entry point for device probing."""
    sys.argv = ["pi-kinect-probe"] + sys.argv[1:]
    main()


def start_streaming_cli() -> None:
    """CLI entry point for streaming."""
    sys.argv = ["pi-kinect-stream"] + sys.argv[1:]
    main()


def start_viewer_cli() -> None:
    """CLI entry point for viewer."""
    sys.argv = ["pi-kinect-viewer"] + sys.argv[1:]
    main()


if __name__ == "__main__":
    main()
