"""
Base Route Class

This module provides a base class for all route handlers in the application.
It includes common functionality and utilities that can be reused across different routes.
"""

import json
import gzip
import time
import logging
from datetime import datetime
from functools import wraps
from typing import Any, Callable, Dict, Optional, Union, List, Tuple

from flask import Blueprint, render_template, request, jsonify, current_app, Response
from werkzeug.exceptions import HTTPException

from ..services.performance_monitor import performance_monitor
from ..services.cache_service import cache_service

class BaseRoute:
    """Base class for all route handlers."""
    
    def __init__(self, name: str, url_prefix: str = ''):
        """
        Initialize the base route.
        
        Args:
            name: The name of the route
            url_prefix: URL prefix for all routes in this blueprint
        """
        self.name = name
        self.blueprint = Blueprint(name, __name__, url_prefix=url_prefix)
        self.logger = logging.getLogger(f"frontend.routes.{name}")
        
        # Register error handlers
        self.register_error_handlers()
        
    def register_error_handlers(self) -> None:
        """Register error handlers for the blueprint."""
        @self.blueprint.errorhandler(404)
        def not_found_error(error):
            self.logger.error(f"404 error: {request.url}")
            return self.json_response({'error': 'Not found'}, 404)
            
        @self.blueprint.errorhandler(500)
        def internal_error(error):
            self.logger.error(f"500 error: {str(error)}")
            return self.json_response({'error': 'Internal server error'}, 500)
            
    def handle_errors(self, f: Callable) -> Callable:
        """
        Decorator for handling errors in route functions.
        
        Args:
            f: The route function to wrap
            
        Returns:
            The wrapped function
        """
        @wraps(f)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            endpoint = f"{self.name}.{f.__name__}"
            
            try:
                result = f(*args, **kwargs)
                duration = time.time() - start_time
                
                # Record performance metric
                performance_monitor.record_metric(
                    name="response_time",
                    value=duration,
                    endpoint=endpoint,
                    context={
                        'method': request.method,
                        'path': request.path,
                        'status_code': 200 if hasattr(result, 'status_code') else None
                    }
                )
                
                return result
            except HTTPException as e:
                duration = time.time() - start_time
                self.logger.error(f"HTTP error in {endpoint}: {str(e)} (took {duration:.2f}s)")
                
                performance_monitor.record_metric(
                    name="response_time",
                    value=duration,
                    endpoint=endpoint,
                    context={
                        'method': request.method,
                        'path': request.path,
                        'status_code': e.code,
                        'error': str(e)
                    }
                )
                
                return self.json_response({'error': str(e)}, e.code)
            except Exception as e:
                duration = time.time() - start_time
                self.logger.error(f"Error in {endpoint}: {str(e)} (took {duration:.2f}s)")
                
                performance_monitor.record_metric(
                    name="response_time",
                    value=duration,
                    endpoint=endpoint,
                    context={
                        'method': request.method,
                        'path': request.path,
                        'status_code': 500,
                        'error': str(e)
                    }
                )
                
                return self.json_response({'error': 'Internal server error'}, 500)
        return wrapper
        
    def render_template(self, template: str, **kwargs) -> str:
        """
        Render a template with common context.
        
        Args:
            template: The template to render
            **kwargs: Additional context variables
            
        Returns:
            The rendered template
        """
        try:
            # Add common context variables
            context = {
                'current_route': self.name,
                'request': request,
                'timestamp': datetime.now().isoformat(),
                **kwargs
            }
            return render_template(template, **context)
        except Exception as e:
            self.logger.error(f"Error rendering template {template}: {str(e)}")
            return self.json_response({'error': 'Template rendering failed'}, 500)
            
    def json_response(self, data: Any, status: int = 200, compress: bool = False) -> Union[Tuple[Response, int], Response]:
        """
        Return a JSON response.
        
        Args:
            data: The data to return
            status: The HTTP status code
            compress: Whether to compress the response
            
        Returns:
            A tuple of (response, status_code) or a Response object
        """
        if compress:
            return self.compressed_response(data, status)
        return jsonify(data), status
        
    def compressed_response(self, data: Any, status: int = 200) -> Response:
        """
        Return a compressed JSON response.
        
        Args:
            data: The data to return
            status: The HTTP status code
            
        Returns:
            A compressed Response object
        """
        json_data = json.dumps(data)
        gzip_data = gzip.compress(json_data.encode('utf-8'))
        response = Response(gzip_data, status=status)
        response.headers['Content-Type'] = 'application/json'
        response.headers['Content-Encoding'] = 'gzip'
        response.headers['Vary'] = 'Accept-Encoding'
        return response
        
    def get_request_data(self) -> Dict:
        """
        Get data from the request.
        
        Returns:
            The request data as a dictionary
        """
        if request.is_json:
            return request.get_json()
        return request.form.to_dict()
        
    def validate_required_fields(self, data: Dict, required_fields: list) -> Optional[str]:
        """
        Validate that all required fields are present in the data.
        
        Args:
            data: The data to validate
            required_fields: List of required field names
            
        Returns:
            Error message if validation fails, None otherwise
        """
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return f"Missing required fields: {', '.join(missing_fields)}"
        return None
        
    def cache_with_ttl(self, ttl: int = None) -> Callable:
        """
        Decorator for caching function results with a time-to-live.
        
        Args:
            ttl: Time-to-live in seconds
            
        Returns:
            A decorator function
        """
        return cache_service.cached(ttl)
        
    def clear_cache(self) -> None:
        """Clear the route's cache."""
        cache_service.clear()
        self.logger.info(f"Cache cleared for {self.name}")
        
    def format_datetime(self, dt: datetime) -> str:
        """
        Format a datetime object for JSON serialization.
        
        Args:
            dt: The datetime to format
            
        Returns:
            Formatted datetime string
        """
        return dt.isoformat() if dt else None
        
    def format_for_json(self, obj: Any) -> Any:
        """
        Format an object for JSON serialization.
        
        Args:
            obj: The object to format
            
        Returns:
            JSON-serializable object
        """
        if isinstance(obj, datetime):
            return self.format_datetime(obj)
        elif isinstance(obj, (list, tuple)):
            return [self.format_for_json(item) for item in obj]
        elif isinstance(obj, dict):
            return {k: self.format_for_json(v) for k, v in obj.items()}
        return obj 