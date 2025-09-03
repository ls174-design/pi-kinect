"""
Logging configuration for Pi-Kinect.

Provides structured logging setup with proper formatting,
file rotation, and per-module loggers.
"""

import logging
import logging.handlers
from pathlib import Path
from typing import Optional
from .config import LoggingConfig


def setup_logging(config: LoggingConfig, logger_name: str = "pi_kinect") -> logging.Logger:
    """
    Set up logging configuration.
    
    Args:
        config: Logging configuration
        logger_name: Name of the main logger
        
    Returns:
        Configured logger instance
    """
    # Create main logger
    logger = logging.getLogger(logger_name)
    logger.setLevel(getattr(logging, config.level.upper()))
    
    # Clear any existing handlers
    logger.handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter(config.format)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, config.level.upper()))
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (if specified)
    if config.file:
        file_path = Path(config.file)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.handlers.RotatingFileHandler(
            config.file,
            maxBytes=config.max_size,
            backupCount=config.backup_count
        )
        file_handler.setLevel(getattr(logging, config.level.upper()))
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    # Prevent propagation to root logger
    logger.propagate = False
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger for a specific module.
    
    Args:
        name: Module name (usually __name__)
        
    Returns:
        Logger instance
    """
    return logging.getLogger(f"pi_kinect.{name}")


class LoggerMixin:
    """Mixin class to add logging capabilities to any class."""
    
    @property
    def logger(self) -> logging.Logger:
        """Get logger for this class."""
        return get_logger(self.__class__.__module__)
