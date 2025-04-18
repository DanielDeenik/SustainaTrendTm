"""
Configuration Service for SustainaTrend™

This module provides a centralized configuration service that loads settings from
environment variables and provides a consistent interface for accessing them.
"""

import os
import logging
from typing import Any, Dict, Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logger
logger = logging.getLogger(__name__)

class ConfigService:
    """
    Singleton class for managing application configuration.
    
    This service loads configuration from environment variables and provides
    a consistent interface for accessing them. It also includes default values
    for all settings to ensure the application can run even if some environment
    variables are missing.
    """
    
    _instance = None
    _config = None
    
    def __new__(cls):
        """Ensure only one instance of ConfigService exists."""
        if cls._instance is None:
            cls._instance = super(ConfigService, cls).__new__(cls)
            cls._instance._load_config()
        return cls._instance
    
    def _load_config(self):
        """Load configuration from environment variables."""
        self._config = {
            # Application Configuration
            'SECRET_KEY': os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production'),
            'DEBUG': os.getenv('DEBUG', 'True').lower() == 'true',
            'PORT': int(os.getenv('PORT', '5000')),
            'HOST': os.getenv('HOST', '127.0.0.1'),
            
            # Database Configuration
            'MONGODB_URI': os.getenv('MONGODB_URI', 'mongodb://localhost:27017/'),
            'MONGODB_DATABASE': os.getenv('MONGODB_DATABASE', 'sustainatrend'),
            'USE_MOCK_MONGODB': os.getenv('USE_MOCK_MONGODB', 'False').lower() == 'true',
            
            # API Configuration
            'API_VERSION': os.getenv('API_VERSION', 'v1'),
            'API_PREFIX': os.getenv('API_PREFIX', '/api'),
            
            # Logging Configuration
            'LOG_LEVEL': os.getenv('LOG_LEVEL', 'INFO'),
            'LOG_FILE': os.getenv('LOG_FILE', 'logs/app.log'),
            
            # Cache Configuration
            'CACHE_TYPE': os.getenv('CACHE_TYPE', 'simple'),
            'CACHE_DEFAULT_TIMEOUT': int(os.getenv('CACHE_DEFAULT_TIMEOUT', '300')),
            
            # Security Configuration
            'SESSION_COOKIE_SECURE': os.getenv('SESSION_COOKIE_SECURE', 'False').lower() == 'true',
            'SESSION_COOKIE_HTTPONLY': os.getenv('SESSION_COOKIE_HTTPONLY', 'True').lower() == 'true',
            'SESSION_COOKIE_SAMESITE': os.getenv('SESSION_COOKIE_SAMESITE', 'Lax'),
            'JWT_SECRET_KEY': os.getenv('JWT_SECRET_KEY', 'your-jwt-secret-key-change-in-production'),
            'BCRYPT_LOG_ROUNDS': int(os.getenv('BCRYPT_LOG_ROUNDS', '12')),
            
            # Flask Configuration
            'FLASK_DEBUG': os.getenv('FLASK_DEBUG', '1'),
            'FLASK_APP': os.getenv('FLASK_APP', 'src/frontend/refactored/app.py'),
            
            # API Keys
            'GOOGLE_API_KEY': os.getenv('GOOGLE_API_KEY', ''),
            'GOOGLE_CSE_ID': os.getenv('GOOGLE_CSE_ID', ''),
            'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY', ''),
            
            # Vector Database Configuration
            'VECTOR_DB_PATH': os.getenv('VECTOR_DB_PATH', './vector_db'),
            'VECTOR_DB_COLLECTION': os.getenv('VECTOR_DB_COLLECTION', 'sustainatrend_collection'),
            
            # File Upload Configuration
            'UPLOAD_FOLDER': os.getenv('UPLOAD_FOLDER', 'uploads'),
            'MAX_CONTENT_LENGTH': self._parse_max_content_length(),
            
            # MongoDB Atlas Credentials
            'MONGODB_USERNAME': os.getenv('MONGODB_USERNAME', ''),
            'MONGODB_PASSWORD': os.getenv('MONGODB_PASSWORD', ''),
            
            # Session Configuration
            'SESSION_TYPE': os.getenv('SESSION_TYPE', 'filesystem'),
            'SESSION_PERMANENT': os.getenv('SESSION_PERMANENT', 'False').lower() == 'true',
            'PERMANENT_SESSION_LIFETIME': int(os.getenv('PERMANENT_SESSION_LIFETIME', '3600')),
            
            # Email Configuration
            'MAIL_SERVER': os.getenv('MAIL_SERVER', 'smtp.gmail.com'),
            'MAIL_PORT': int(os.getenv('MAIL_PORT', '587')),
            'MAIL_USE_TLS': os.getenv('MAIL_USE_TLS', 'True').lower() == 'true',
            'MAIL_USERNAME': os.getenv('MAIL_USERNAME', ''),
            'MAIL_PASSWORD': os.getenv('MAIL_PASSWORD', ''),
            
            # Additional Configuration
            'SENTRY_DSN': os.getenv('SENTRY_DSN', ''),
            'ADMIN_KEY': os.getenv('ADMIN_KEY', 'dev-admin-key-change-in-production'),
            'VERSION': os.getenv('VERSION', '1.0.0')
        }
        
        # Validate configuration
        self._validate_config()
    
    def _parse_max_content_length(self) -> int:
        """Parse MAX_CONTENT_LENGTH from environment variable."""
        try:
            value = os.getenv('MAX_CONTENT_LENGTH', '16777216')  # Default 16MB
            # Remove any comments and whitespace
            value = value.split('#')[0].strip()
            # Convert to integer
            value = int(value)
            if value <= 0:
                raise ValueError("MAX_CONTENT_LENGTH must be positive")
            return value
        except (ValueError, TypeError):
            logger.warning("Invalid MAX_CONTENT_LENGTH value. Using default of 16MB.")
            return 16777216  # 16MB in bytes
        
    def _validate_config(self):
        """Validate configuration values."""
        # Validate FLASK_DEBUG
        flask_debug = self._config['FLASK_DEBUG']
        if flask_debug not in ['0', '1']:
            logger.warning("Invalid FLASK_DEBUG value. Using default of '0'.")
            self._config['FLASK_DEBUG'] = '0'
        
        # Log configuration status
        logger.info(f"Configuration loaded. Debug mode: {self.is_debug()}")
        logger.info(f"Max content length: {self.get_max_content_length()} bytes")
    
    def get_config(self):
        """Get the entire configuration dictionary."""
        return self._config
    
    def get(self, key, default=None):
        """Get a configuration value."""
        return self._config.get(key, default)
    
    def get_mongodb_uri(self):
        """Get MongoDB connection URI with credentials if provided."""
        uri = self._config['MONGODB_URI']
        
        # Don't add authentication for local MongoDB
        if uri.startswith('mongodb://localhost'):
            return uri
            
        username = self._config['MONGODB_USERNAME']
        password = self._config['MONGODB_PASSWORD']
        
        if username and password:
            # Extract the protocol and host parts
            if '://' in uri:
                protocol, rest = uri.split('://', 1)
                return f"{protocol}://{username}:{password}@{rest}"
            else:
                return f"mongodb://{username}:{password}@{uri}"
        
        return uri
    
    def get_mongodb_db(self):
        """Get MongoDB database name."""
        return self._config['MONGODB_DATABASE']
    
    def is_debug(self):
        """Check if debug mode is enabled."""
        return self._config['FLASK_DEBUG'] == '1'
    
    def get_host(self):
        """Get the host to bind to."""
        return self._config['HOST']
    
    def get_port(self):
        """Get the port to bind to."""
        return self._config['PORT']
    
    def get_version(self):
        """Get the application version."""
        return self._config['VERSION']
    
    def get_admin_key(self):
        """Get the admin key."""
        return self._config['ADMIN_KEY']
    
    def get_upload_folder(self):
        """Get the upload folder path."""
        return self._config['UPLOAD_FOLDER']
    
    def get_max_content_length(self):
        """Get the maximum content length in bytes."""
        return self._config['MAX_CONTENT_LENGTH']

# Create a singleton instance
config_service = ConfigService()

# Export the singleton instance
__all__ = ['config_service'] 