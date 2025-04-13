"""
SustainaTrend Configuration Settings

This module contains all configuration settings for the SustainaTrend platform.
Settings are loaded from environment variables with fallback to default values.
"""

import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"
BACKEND_DIR = BASE_DIR / "backend"
DATA_DIR = BASE_DIR / "data"

# Database settings
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", "sustainatrend")
VECTOR_DB_PATH = os.getenv("VECTOR_DB_PATH", str(DATA_DIR / "vector_db"))
VECTOR_DB_COLLECTION = os.getenv("VECTOR_DB_COLLECTION", "sustainatrend_vectors")

# API settings
API_VERSION = "v1"
API_PREFIX = f"/api/{API_VERSION}"
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# Security settings
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")

# Logging settings
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_FILE = BASE_DIR / "logs" / "sustainatrend.log"

# Cache settings
CACHE_TYPE = os.getenv("CACHE_TYPE", "simple")
CACHE_DEFAULT_TIMEOUT = int(os.getenv("CACHE_DEFAULT_TIMEOUT", "300"))

# Feature flags
ENABLE_VECTOR_SEARCH = os.getenv("ENABLE_VECTOR_SEARCH", "True").lower() == "true"
ENABLE_REAL_TIME_UPDATES = os.getenv("ENABLE_REAL_TIME_UPDATES", "True").lower() == "true"

# Create necessary directories
for directory in [DATA_DIR, LOG_FILE.parent]:
    directory.mkdir(parents=True, exist_ok=True) 