"""
Logging Configuration Module

This module configures logging for the SustainaTrend platform.
"""

import logging
import logging.handlers
import sys
from pathlib import Path

from .settings import LOG_FILE, LOG_FORMAT, LOG_LEVEL

# Create logs directory if it doesn't exist
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

# Configure root logger
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format=LOG_FORMAT,
    handlers=[
        # Console handler
        logging.StreamHandler(sys.stdout),
        # File handler with rotation
        logging.handlers.RotatingFileHandler(
            LOG_FILE,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding="utf-8",
        ),
    ],
)

# Create logger for the application
logger = logging.getLogger("sustainatrend")

# Suppress overly verbose logs from external libraries
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("chromadb").setLevel(logging.WARNING)
logging.getLogger("pymongo").setLevel(logging.WARNING)

def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the given name."""
    return logging.getLogger(f"sustainatrend.{name}") 