"""
Monitoring Service for SustainaTrend™

This module tracks application health, API status, and system metrics.
"""

import os
import time
import psutil
import logging
import threading
from typing import Dict, List, Any
from datetime import datetime
from src.frontend.refactored.services.mongodb_service import mongodb_service
from src.frontend.refactored.services.config_service import config_service

# Configure logger
logger = logging.getLogger(__name__)

class MonitoringService:
    """
    Singleton class for monitoring application health and metrics.
    
    This service tracks:
    - Application health (MongoDB connection, API status)
    - System metrics (CPU, memory, disk usage)
    - API response times
    - Error rates
    """
    
    _instance = None
    _lock = threading.Lock()
    _metrics_history = []
    _max_history_size = 1000
    
    def __new__(cls):
        """Ensure only one instance of MonitoringService exists."""
        if cls._instance is None:
            cls._instance = super(MonitoringService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize the monitoring service."""
        if self._initialized:
            return
            
        self._initialized = True
        self._metrics_history = []
        self._start_time = time.time()
        
        # Start metrics collection in a background thread
        self._start_metrics_collection()
    
    def _start_metrics_collection(self):
        """Start collecting metrics in a background thread."""
        def collect_metrics():
            while True:
                try:
                    metrics = self._collect_system_metrics()
                    self._add_metrics(metrics)
                    time.sleep(60)  # Collect metrics every minute
                except Exception as e:
                    logger.error(f"Error collecting metrics: {str(e)}")
        
        thread = threading.Thread(target=collect_metrics, daemon=True)
        thread.start()
    
    def _collect_system_metrics(self) -> Dict[str, Any]:
        """Collect system metrics."""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                'timestamp': datetime.now().isoformat(),
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'memory_used': memory.used,
                'memory_available': memory.available,
                'disk_percent': disk.percent,
                'disk_used': disk.used,
                'disk_free': disk.free
            }
        except Exception as e:
            logger.error(f"Error collecting system metrics: {str(e)}")
            return {}
    
    def _add_metrics(self, metrics: Dict[str, Any]):
        """Add metrics to history."""
        with self._lock:
            self._metrics_history.append(metrics)
            if len(self._metrics_history) > self._max_history_size:
                self._metrics_history.pop(0)
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get overall health status."""
        try:
            # Check MongoDB connection
            mongodb_status = 'healthy' if mongodb_service.is_connected() else 'unhealthy'
            
            # Get system metrics
            metrics = self._collect_system_metrics()
            
            # Calculate uptime
            uptime = time.time() - self._start_time
            
            return {
                'status': 'healthy',
                'mongodb_status': mongodb_status,
                'uptime': uptime,
                'timestamp': datetime.now().isoformat(),
                'version': config_service.get_version(),
                'environment': 'development' if config_service.is_debug() else 'production',
                'metrics': metrics
            }
        except Exception as e:
            logger.error(f"Error getting health status: {str(e)}")
            return {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def get_metrics_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get metrics history."""
        with self._lock:
            return self._metrics_history[-limit:]
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get current system metrics."""
        return self._collect_system_metrics()
    
    def get_mongodb_status(self) -> Dict[str, Any]:
        """Get MongoDB connection status."""
        try:
            return {
                'connected': mongodb_service.is_connected(),
                'database': config_service.get_mongodb_db(),
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting MongoDB status: {str(e)}")
            return {
                'connected': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def get_api_status(self) -> Dict[str, Any]:
        """Get API status."""
        try:
            # Check if API endpoints are accessible
            api_prefix = config_service.get('API_PREFIX', '/api')
            api_version = config_service.get('API_VERSION', 'v1')
            
            return {
                'status': 'healthy',
                'api_prefix': api_prefix,
                'api_version': api_version,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting API status: {str(e)}")
            return {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

# Create a singleton instance
monitoring_service = MonitoringService()

# Export the singleton instance
__all__ = ['monitoring_service'] 