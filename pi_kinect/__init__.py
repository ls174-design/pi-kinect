"""
Pi-Kinect: Raspberry Pi Kinect Streaming Package

A comprehensive solution for streaming Kinect camera feeds from a Raspberry Pi
with automatic fallback to OpenCV and robust error handling.
"""

__version__ = "1.0.0"
__author__ = "Pi-Kinect Team"
__email__ = "team@pi-kinect.dev"

from .streamer import KinectStreamer
from .viewer import CameraViewer
from .config import Config

__all__ = ["KinectStreamer", "CameraViewer", "Config"]
