"""
Configuration management for Pi-Kinect.

Handles loading configuration from YAML files, environment variables,
and command line arguments with proper validation and defaults.
"""

import os
import yaml
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from pathlib import Path


@dataclass
class NetworkConfig:
    """Network configuration settings."""
    host: str = "0.0.0.0"
    port: int = 8080
    timeout: int = 10


@dataclass
class CameraConfig:
    """Camera configuration settings."""
    index: int = 0
    width: int = 640
    height: int = 480
    fps: int = 30
    jpeg_quality: int = 85


@dataclass
class KinectConfig:
    """Kinect-specific configuration."""
    enabled: bool = True
    auto_detect: bool = True
    fallback_to_opencv: bool = True
    depth_enabled: bool = True
    ir_enabled: bool = False


@dataclass
class LoggingConfig:
    """Logging configuration."""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file: Optional[str] = None
    max_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5


@dataclass
class Config:
    """Main configuration class."""
    network: NetworkConfig = field(default_factory=NetworkConfig)
    camera: CameraConfig = field(default_factory=CameraConfig)
    kinect: KinectConfig = field(default_factory=KinectConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    
    # Pi-specific settings
    pi_ip: str = "192.168.1.9"
    pi_username: str = "pi"
    pi_password: Optional[str] = None
    
    # Development settings
    debug: bool = False
    profile: bool = False
    
    @classmethod
    def load(cls, config_path: Optional[str] = None) -> "Config":
        """Load configuration from file and environment variables."""
        config = cls()
        
        # Load from YAML file if provided
        if config_path and Path(config_path).exists():
            config._load_from_file(config_path)
        
        # Override with environment variables
        config._load_from_env()
        
        return config
    
    def _load_from_file(self, config_path: str) -> None:
        """Load configuration from YAML file."""
        try:
            with open(config_path, 'r') as f:
                data = yaml.safe_load(f)
                if data:
                    self._update_from_dict(data)
        except Exception as e:
            print(f"Warning: Failed to load config from {config_path}: {e}")
    
    def _load_from_env(self) -> None:
        """Load configuration from environment variables."""
        # Network settings
        if os.getenv("PI_KINECT_HOST"):
            self.network.host = os.getenv("PI_KINECT_HOST")
        if os.getenv("PI_KINECT_PORT"):
            self.network.port = int(os.getenv("PI_KINECT_PORT"))
        
        # Pi connection settings
        if os.getenv("PI_KINECT_IP"):
            self.pi_ip = os.getenv("PI_KINECT_IP")
        if os.getenv("PI_KINECT_USERNAME"):
            self.pi_username = os.getenv("PI_KINECT_USERNAME")
        if os.getenv("PI_KINECT_PASSWORD"):
            self.pi_password = os.getenv("PI_KINECT_PASSWORD")
        
        # Camera settings
        if os.getenv("PI_KINECT_CAMERA_INDEX"):
            self.camera.index = int(os.getenv("PI_KINECT_CAMERA_INDEX"))
        if os.getenv("PI_KINECT_WIDTH"):
            self.camera.width = int(os.getenv("PI_KINECT_WIDTH"))
        if os.getenv("PI_KINECT_HEIGHT"):
            self.camera.height = int(os.getenv("PI_KINECT_HEIGHT"))
        if os.getenv("PI_KINECT_FPS"):
            self.camera.fps = int(os.getenv("PI_KINECT_FPS"))
        
        # Logging settings
        if os.getenv("PI_KINECT_LOG_LEVEL"):
            self.logging.level = os.getenv("PI_KINECT_LOG_LEVEL")
        if os.getenv("PI_KINECT_LOG_FILE"):
            self.logging.file = os.getenv("PI_KINECT_LOG_FILE")
        
        # Debug settings
        if os.getenv("PI_KINECT_DEBUG"):
            self.debug = os.getenv("PI_KINECT_DEBUG").lower() in ("true", "1", "yes")
    
    def _update_from_dict(self, data: Dict[str, Any]) -> None:
        """Update configuration from dictionary."""
        if "network" in data:
            network_data = data["network"]
            if "host" in network_data:
                self.network.host = network_data["host"]
            if "port" in network_data:
                self.network.port = network_data["port"]
            if "timeout" in network_data:
                self.network.timeout = network_data["timeout"]
        
        if "camera" in data:
            camera_data = data["camera"]
            if "index" in camera_data:
                self.camera.index = camera_data["index"]
            if "width" in camera_data:
                self.camera.width = camera_data["width"]
            if "height" in camera_data:
                self.camera.height = camera_data["height"]
            if "fps" in camera_data:
                self.camera.fps = camera_data["fps"]
            if "jpeg_quality" in camera_data:
                self.camera.jpeg_quality = camera_data["jpeg_quality"]
        
        if "kinect" in data:
            kinect_data = data["kinect"]
            if "enabled" in kinect_data:
                self.kinect.enabled = kinect_data["enabled"]
            if "auto_detect" in kinect_data:
                self.kinect.auto_detect = kinect_data["auto_detect"]
            if "fallback_to_opencv" in kinect_data:
                self.kinect.fallback_to_opencv = kinect_data["fallback_to_opencv"]
            if "depth_enabled" in kinect_data:
                self.kinect.depth_enabled = kinect_data["depth_enabled"]
            if "ir_enabled" in kinect_data:
                self.kinect.ir_enabled = kinect_data["ir_enabled"]
        
        if "logging" in data:
            logging_data = data["logging"]
            if "level" in logging_data:
                self.logging.level = logging_data["level"]
            if "format" in logging_data:
                self.logging.format = logging_data["format"]
            if "file" in logging_data:
                self.logging.file = logging_data["file"]
        
        if "pi_ip" in data:
            self.pi_ip = data["pi_ip"]
        if "pi_username" in data:
            self.pi_username = data["pi_username"]
        if "pi_password" in data:
            self.pi_password = data["pi_password"]
        if "debug" in data:
            self.debug = data["debug"]
        if "profile" in data:
            self.profile = data["profile"]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "network": {
                "host": self.network.host,
                "port": self.network.port,
                "timeout": self.network.timeout
            },
            "camera": {
                "index": self.camera.index,
                "width": self.camera.width,
                "height": self.camera.height,
                "fps": self.camera.fps,
                "jpeg_quality": self.camera.jpeg_quality
            },
            "kinect": {
                "enabled": self.kinect.enabled,
                "auto_detect": self.kinect.auto_detect,
                "fallback_to_opencv": self.kinect.fallback_to_opencv,
                "depth_enabled": self.kinect.depth_enabled,
                "ir_enabled": self.kinect.ir_enabled
            },
            "logging": {
                "level": self.logging.level,
                "format": self.logging.format,
                "file": self.logging.file,
                "max_size": self.logging.max_size,
                "backup_count": self.logging.backup_count
            },
            "pi_ip": self.pi_ip,
            "pi_username": self.pi_username,
            "pi_password": self.pi_password,
            "debug": self.debug,
            "profile": self.profile
        }
    
    def save(self, config_path: str) -> None:
        """Save configuration to YAML file."""
        with open(config_path, 'w') as f:
            yaml.dump(self.to_dict(), f, default_flow_style=False, indent=2)
