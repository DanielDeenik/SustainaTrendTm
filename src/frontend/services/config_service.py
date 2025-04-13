"""
Configuration Service

This module provides centralized configuration management for the application.
"""

import os
import json
import logging
from typing import Any, Dict, Optional
from pathlib import Path
from dataclasses import dataclass

@dataclass
class AppConfig:
    """Application configuration settings."""
    debug: bool = False
    testing: bool = False
    secret_key: str = os.urandom(24).hex()
    
    # Server settings
    host: str = "0.0.0.0"
    port: int = 5000
    
    # Cache settings
    cache_type: str = "simple"
    cache_default_timeout: int = 300
    
    # Performance monitoring
    perf_slow_request_threshold: float = 0.5
    perf_max_history: int = 1000
    perf_cleanup_interval: int = 3600
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    log_file: Optional[str] = None
    
    # Security
    session_type: str = "filesystem"
    session_permanent: bool = False
    permanent_session_lifetime: int = 3600
    
    # API settings
    api_rate_limit: int = 100
    api_rate_limit_period: int = 60
    api_timeout: int = 30
    
    # Feature flags
    enable_compression: bool = True
    enable_caching: bool = True
    enable_performance_monitoring: bool = True

class ConfigService:
    """Service for managing application configuration."""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the configuration service.
        
        Args:
            config_path: Path to the configuration file (optional)
        """
        self.logger = logging.getLogger(__name__)
        self.config = AppConfig()
        
        # Load configuration from environment variables
        self._load_from_env()
        
        # Load configuration from file if provided
        if config_path:
            self._load_from_file(config_path)
            
        # Validate configuration
        self._validate_config()
        
    def _load_from_env(self) -> None:
        """Load configuration from environment variables."""
        for field in AppConfig.__dataclass_fields__:
            env_var = f"APP_{field.upper()}"
            if env_var in os.environ:
                value = os.environ[env_var]
                field_type = type(getattr(self.config, field))
                
                try:
                    if field_type == bool:
                        value = value.lower() in ('true', '1', 'yes')
                    elif field_type == int:
                        value = int(value)
                    elif field_type == float:
                        value = float(value)
                        
                    setattr(self.config, field, value)
                except ValueError as e:
                    self.logger.error(f"Error parsing environment variable {env_var}: {e}")
                    
    def _load_from_file(self, config_path: str) -> None:
        """
        Load configuration from a JSON file.
        
        Args:
            config_path: Path to the configuration file
        """
        try:
            with open(config_path, 'r') as f:
                config_data = json.load(f)
                
            for field, value in config_data.items():
                if hasattr(self.config, field):
                    setattr(self.config, field, value)
                else:
                    self.logger.warning(f"Unknown configuration field: {field}")
        except Exception as e:
            self.logger.error(f"Error loading configuration from {config_path}: {e}")
            
    def _validate_config(self) -> None:
        """Validate the configuration settings."""
        if self.config.api_rate_limit <= 0:
            self.logger.warning("API rate limit must be positive, setting to default (100)")
            self.config.api_rate_limit = 100
            
        if self.config.api_timeout <= 0:
            self.logger.warning("API timeout must be positive, setting to default (30)")
            self.config.api_timeout = 30
            
        if self.config.cache_default_timeout <= 0:
            self.logger.warning("Cache timeout must be positive, setting to default (300)")
            self.config.cache_default_timeout = 300
            
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.
        
        Args:
            key: Configuration key
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        return getattr(self.config, key, default)
        
    def set(self, key: str, value: Any) -> None:
        """
        Set a configuration value.
        
        Args:
            key: Configuration key
            value: Value to set
        """
        if hasattr(self.config, key):
            setattr(self.config, key, value)
        else:
            self.logger.warning(f"Attempted to set unknown configuration key: {key}")
            
    def to_dict(self) -> Dict:
        """
        Convert configuration to dictionary.
        
        Returns:
            Dictionary of configuration values
        """
        return {
            field: getattr(self.config, field)
            for field in AppConfig.__dataclass_fields__
        }
        
    def save_to_file(self, config_path: str) -> None:
        """
        Save configuration to a JSON file.
        
        Args:
            config_path: Path to save the configuration file
        """
        try:
            config_dir = os.path.dirname(config_path)
            if config_dir:
                os.makedirs(config_dir, exist_ok=True)
                
            with open(config_path, 'w') as f:
                json.dump(self.to_dict(), f, indent=4)
                
            self.logger.info(f"Configuration saved to {config_path}")
        except Exception as e:
            self.logger.error(f"Error saving configuration to {config_path}: {e}")
            
# Create a global instance
config_service = ConfigService() 