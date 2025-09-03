"""
Custom exceptions for Pi-Kinect package.
"""


class PiKinectError(Exception):
    """Base exception for all Pi-Kinect errors."""
    pass


class DeviceNotFoundError(PiKinectError):
    """Raised when a required device (Kinect, camera) is not found."""
    pass


class StreamError(PiKinectError):
    """Raised when streaming operations fail."""
    pass


class ConfigurationError(PiKinectError):
    """Raised when configuration is invalid or missing."""
    pass


class NetworkError(PiKinectError):
    """Raised when network operations fail."""
    pass


class FreenectError(PiKinectError):
    """Raised when freenect operations fail."""
    pass


class OpenCVError(PiKinectError):
    """Raised when OpenCV operations fail."""
    pass
