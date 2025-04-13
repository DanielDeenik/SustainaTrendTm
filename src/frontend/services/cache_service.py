"""
Cache Service

This module provides caching functionality for the application.
"""

import time
import logging
import threading
from typing import Any, Dict, Optional, Tuple
from datetime import datetime, timedelta
from functools import wraps

class CacheService:
    """Service for handling application-wide caching."""
    
    def __init__(self, default_ttl: int = 300):
        """
        Initialize the cache service.
        
        Args:
            default_ttl: Default time-to-live in seconds (default: 5 minutes)
        """
        self.logger = logging.getLogger(__name__)
        self.cache: Dict[str, Tuple[Any, float]] = {}
        self.default_ttl = default_ttl
        self.lock = threading.Lock()
        
    def get(self, key: str) -> Optional[Any]:
        """
        Get a value from the cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value if found and not expired, None otherwise
        """
        with self.lock:
            if key not in self.cache:
                return None
                
            value, expiry = self.cache[key]
            if time.time() > expiry:
                del self.cache[key]
                return None
                
            return value
            
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Set a value in the cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (optional)
        """
        expiry = time.time() + (ttl or self.default_ttl)
        with self.lock:
            self.cache[key] = (value, expiry)
            
    def delete(self, key: str) -> None:
        """
        Delete a value from the cache.
        
        Args:
            key: Cache key
        """
        with self.lock:
            self.cache.pop(key, None)
            
    def clear(self) -> None:
        """Clear all cached values."""
        with self.lock:
            self.cache.clear()
            
    def cleanup(self) -> None:
        """Remove expired entries from the cache."""
        now = time.time()
        with self.lock:
            expired = [k for k, (_, exp) in self.cache.items() if exp <= now]
            for key in expired:
                del self.cache[key]
                
    def cached(self, ttl: Optional[int] = None):
        """
        Decorator for caching function results.
        
        Args:
            ttl: Time-to-live in seconds (optional)
            
        Returns:
            Decorated function
        """
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Create cache key from function name and arguments
                key = f"{func.__module__}.{func.__name__}:{str(args)}:{str(kwargs)}"
                
                # Try to get from cache
                cached_value = self.get(key)
                if cached_value is not None:
                    self.logger.debug(f"Cache hit for {key}")
                    return cached_value
                    
                # Call function and cache result
                result = func(*args, **kwargs)
                self.set(key, result, ttl)
                self.logger.debug(f"Cache miss for {key}")
                return result
            return wrapper
        return decorator
        
    def get_stats(self) -> Dict:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        with self.lock:
            total_entries = len(self.cache)
            now = time.time()
            expired = sum(1 for _, exp in self.cache.values() if exp <= now)
            
        return {
            "total_entries": total_entries,
            "expired_entries": expired,
            "active_entries": total_entries - expired,
            "timestamp": datetime.now().isoformat()
        }
        
# Create a global instance
cache_service = CacheService() 