"""
Tests for configuration management.
"""

import pytest
import tempfile
import os
from pathlib import Path

from pi_kinect.config import Config, NetworkConfig, CameraConfig, KinectConfig


class TestConfig:
    """Test configuration loading and management."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = Config()
        
        assert config.network.host == "0.0.0.0"
        assert config.network.port == 8080
        assert config.camera.width == 640
        assert config.camera.height == 480
        assert config.kinect.enabled is True
    
    def test_config_from_file(self):
        """Test loading configuration from YAML file."""
        yaml_content = """
network:
  host: "192.168.1.100"
  port: 9000
camera:
  width: 1280
  height: 720
kinect:
  enabled: false
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(yaml_content)
            temp_path = f.name
        
        try:
            config = Config.load(temp_path)
            
            assert config.network.host == "192.168.1.100"
            assert config.network.port == 9000
            assert config.camera.width == 1280
            assert config.camera.height == 720
            assert config.kinect.enabled is False
        finally:
            os.unlink(temp_path)
    
    def test_config_from_env(self):
        """Test loading configuration from environment variables."""
        # Set environment variables
        os.environ["PI_KINECT_HOST"] = "192.168.1.200"
        os.environ["PI_KINECT_PORT"] = "9001"
        os.environ["PI_KINECT_CAMERA_INDEX"] = "2"
        
        try:
            config = Config.load()
            
            assert config.network.host == "192.168.1.200"
            assert config.network.port == 9001
            assert config.camera.index == 2
        finally:
            # Clean up environment variables
            for key in ["PI_KINECT_HOST", "PI_KINECT_PORT", "PI_KINECT_CAMERA_INDEX"]:
                os.environ.pop(key, None)
    
    def test_config_save_and_load(self):
        """Test saving and loading configuration."""
        config = Config()
        config.network.host = "test.example.com"
        config.camera.width = 1920
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            temp_path = f.name
        
        try:
            config.save(temp_path)
            loaded_config = Config.load(temp_path)
            
            assert loaded_config.network.host == "test.example.com"
            assert loaded_config.camera.width == 1920
        finally:
            os.unlink(temp_path)
    
    def test_config_to_dict(self):
        """Test converting configuration to dictionary."""
        config = Config()
        config_dict = config.to_dict()
        
        assert isinstance(config_dict, dict)
        assert "network" in config_dict
        assert "camera" in config_dict
        assert "kinect" in config_dict
        assert config_dict["network"]["host"] == "0.0.0.0"
        assert config_dict["camera"]["width"] == 640
