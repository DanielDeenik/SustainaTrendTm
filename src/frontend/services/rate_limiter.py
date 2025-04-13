"""
Rate Limiter Service

This module provides rate limiting functionality for the application.
"""

import time
import logging
import threading
from typing import Dict, Optional, Tuple
from collections import defaultdict
from dataclasses import dataclass
from functools import wraps

from flask import request, jsonify
from werkzeug.exceptions import TooManyRequests

from .config_service import config_service

@dataclass
class RateLimit:
    """Rate limit configuration."""
    requests: int
    period: int  # in seconds
    
@dataclass
class RateLimitState:
    """Rate limit state for a key."""
    count: int = 0
    window_start: float = 0.0

class RateLimiter:
    """Service for handling API rate limiting."""
    
    def __init__(self):
        """Initialize the rate limiter."""
        self.logger = logging.getLogger(__name__)
        self.limits: Dict[str, RateLimit] = {}
        self.states: Dict[str, Dict[str, RateLimitState]] = defaultdict(dict)
        self.lock = threading.Lock()
        
        # Set default rate limit from config
        self.set_limit(
            "default",
            config_service.get("api_rate_limit", 100),
            config_service.get("api_rate_limit_period", 60)
        )
        
    def set_limit(self, key: str, requests: int, period: int) -> None:
        """
        Set a rate limit for a key.
        
        Args:
            key: Rate limit key (e.g., 'default', 'api', etc.)
            requests: Number of requests allowed
            period: Time period in seconds
        """
        self.limits[key] = RateLimit(requests=requests, period=period)
        
    def get_client_identifier(self) -> str:
        """
        Get a unique identifier for the current client.
        
        Returns:
            Client identifier string
        """
        # Use X-Forwarded-For header if behind a proxy
        if 'X-Forwarded-For' in request.headers:
            return request.headers.getlist("X-Forwarded-For")[0]
        return request.remote_addr
        
    def is_rate_limited(self, key: str = "default") -> Tuple[bool, Optional[int]]:
        """
        Check if the current request should be rate limited.
        
        Args:
            key: Rate limit key
            
        Returns:
            Tuple of (is_limited, retry_after)
        """
        if key not in self.limits:
            key = "default"
            
        limit = self.limits[key]
        client_id = self.get_client_identifier()
        now = time.time()
        
        with self.lock:
            # Get or create state for this client
            if client_id not in self.states[key]:
                self.states[key][client_id] = RateLimitState(window_start=now)
                
            state = self.states[key][client_id]
            
            # Check if we need to reset the window
            if now - state.window_start >= limit.period:
                state.count = 0
                state.window_start = now
                
            # Check if we're over the limit
            if state.count >= limit.requests:
                retry_after = int(state.window_start + limit.period - now)
                return True, retry_after
                
            # Increment the counter
            state.count += 1
            return False, None
            
    def rate_limit(self, key: str = "default"):
        """
        Decorator for rate limiting routes.
        
        Args:
            key: Rate limit key
            
        Returns:
            Decorated function
        """
        def decorator(f):
            @wraps(f)
            def wrapper(*args, **kwargs):
                is_limited, retry_after = self.is_rate_limited(key)
                
                if is_limited:
                    self.logger.warning(
                        f"Rate limit exceeded for {self.get_client_identifier()} on {key}"
                    )
                    
                    response = jsonify({
                        'error': 'Too many requests',
                        'retry_after': retry_after
                    })
                    response.status_code = 429
                    response.headers['Retry-After'] = str(retry_after)
                    return response
                    
                return f(*args, **kwargs)
            return wrapper
        return decorator
        
    def cleanup(self) -> None:
        """Remove expired rate limit states."""
        now = time.time()
        with self.lock:
            for key in list(self.states.keys()):
                if key in self.limits:
                    limit = self.limits[key]
                    # Remove states older than twice the period
                    expired = [
                        client_id
                        for client_id, state in self.states[key].items()
                        if now - state.window_start >= limit.period * 2
                    ]
                    for client_id in expired:
                        del self.states[key][client_id]
                        
    def get_limits(self) -> Dict:
        """
        Get current rate limits.
        
        Returns:
            Dictionary of rate limits
        """
        return {
            key: {'requests': limit.requests, 'period': limit.period}
            for key, limit in self.limits.items()
        }
        
    def get_state(self, key: str = "default") -> Dict:
        """
        Get current rate limit state.
        
        Args:
            key: Rate limit key
            
        Returns:
            Dictionary of rate limit states
        """
        if key not in self.limits:
            return {}
            
        with self.lock:
            now = time.time()
            return {
                client_id: {
                    'requests_remaining': max(
                        0,
                        self.limits[key].requests - state.count
                    ),
                    'window_expires_in': max(
                        0,
                        int(state.window_start + self.limits[key].period - now)
                    )
                }
                for client_id, state in self.states[key].items()
            }
            
# Create a global instance
rate_limiter = RateLimiter() 