"""
API Routes

This module contains the API routes for the frontend application.
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

from flask import Blueprint, render_template, request
from werkzeug.exceptions import HTTPException

from .base import BaseRoute
from ..utils.navigation_config import get_context_for_template
from ..utils.data_providers import (
    get_metrics,
    get_stories
)
from ..services.performance_monitor import performance_monitor
from ..services.cache_service import cache_service
from ..services.rate_limiter import rate_limiter
from ..services.config_service import config_service

class APIRoute(BaseRoute):
    """API route handler."""
    
    def __init__(self):
        """Initialize the API route."""
        super().__init__('api')
        
        # Set up rate limits
        rate_limiter.set_limit('metrics', 100, 60)  # 100 requests per minute
        rate_limiter.set_limit('status', 300, 60)   # 300 requests per minute
        rate_limiter.set_limit('trends', 100, 60)   # 100 requests per minute
        rate_limiter.set_limit('content', 50, 60)   # 50 requests per minute
        rate_limiter.set_limit('search', 200, 60)   # 200 requests per minute
        
        self.register_routes()
        
    def register_routes(self) -> None:
        """Register all routes for the API blueprint."""
        
        # Metrics and Status Routes
        @self.blueprint.route('/metrics')
        @self.handle_errors
        @rate_limiter.rate_limit('metrics')
        @cache_service.cached(ttl=300)  # Cache for 5 minutes
        def get_metrics_route():
            """Get sustainability metrics."""
            metrics = get_metrics()
            return self.json_response({
                'status': 'success',
                'metrics': metrics,
                'timestamp': datetime.now()
            }, compress=config_service.get('enable_compression', True))
            
        @self.blueprint.route('/status')
        @self.handle_errors
        @rate_limiter.rate_limit('status')
        @cache_service.cached(ttl=60)  # Cache for 1 minute
        def get_status():
            """Get API status."""
            perf_stats = performance_monitor.get_performance_report()
            rate_limits = rate_limiter.get_limits()
            rate_states = {
                key: rate_limiter.get_state(key)
                for key in rate_limits.keys()
            }
            
            return self.json_response({
                'status': 'success',
                'performance': perf_stats,
                'cache_stats': cache_service.get_stats(),
                'rate_limits': rate_limits,
                'rate_states': rate_states,
                'timestamp': datetime.now()
            }, compress=config_service.get('enable_compression', True))
            
        @self.blueprint.route('/trends')
        @self.handle_errors
        @rate_limiter.rate_limit('trends')
        @cache_service.cached(ttl=300)  # Cache for 5 minutes
        def get_trends():
            """Get sustainability trends."""
            return self.json_response({
                'status': 'success',
                'trends': {
                    'emissions_trend': [65, 70, 68, 72, 69, 78.5],
                    'energy_trend': [380, 360, 350, 345, 348, 342],
                    'water_trend': [1.4, 1.35, 1.32, 1.3, 1.29, 1.28]
                },
                'timestamp': datetime.now()
            }, compress=config_service.get('enable_compression', True))
            
        # Content Generation Routes
        @self.blueprint.route('/storytelling', methods=['POST'])
        @self.handle_errors
        @rate_limiter.rate_limit('content')
        def generate_story():
            """Generate a sustainability story based on metrics."""
            data = self.get_request_data()
            required_fields = ['metrics', 'story_type']
            
            error = self.validate_required_fields(data, required_fields)
            if error:
                return self.json_response({'error': error}, 400)
                
            stories = get_stories()
            return self.json_response({
                'status': 'success',
                'story': stories.get(data['story_type'], ''),
                'timestamp': datetime.now()
            }, compress=config_service.get('enable_compression', True))
            
        @self.blueprint.route('/monetization-strategy', methods=['POST'])
        @self.handle_errors
        @rate_limiter.rate_limit('content')
        def generate_monetization_strategy():
            """Generate a monetization strategy based on metrics."""
            data = self.get_request_data()
            required_fields = ['metrics', 'strategy_type']
            
            error = self.validate_required_fields(data, required_fields)
            if error:
                return self.json_response({'error': error}, 400)
                
            return self.json_response({
                'status': 'success',
                'strategy': {
                    'type': data['strategy_type'],
                    'recommendations': [
                        'Implement carbon credits trading',
                        'Develop sustainable product lines',
                        'Create green financing options'
                    ]
                },
                'timestamp': datetime.now()
            }, compress=config_service.get('enable_compression', True))
            
        # Search and Suggestions Routes
        @self.blueprint.route('/omniparser/suggestions')
        @self.handle_errors
        @rate_limiter.rate_limit('search')
        @cache_service.cached(ttl=60)  # Cache for 1 minute
        def get_suggestions():
            """Get search suggestions."""
            query = self.get_request_data().get('query', '').lower()
            
            suggestions = [
                'Carbon Emissions',
                'Energy Usage',
                'Water Conservation',
                'Waste Management',
                'Sustainable Products',
                'Green Financing'
            ]
            
            filtered_suggestions = [
                s for s in suggestions
                if query in s.lower()
            ][:5]
            
            return self.json_response({
                'status': 'success',
                'suggestions': filtered_suggestions,
                'timestamp': datetime.now()
            }, compress=config_service.get('enable_compression', True))
            
        # Monitoring and Maintenance Routes
        @self.blueprint.route('/log-error', methods=['POST'])
        @self.handle_errors
        @rate_limiter.rate_limit('default')
        def log_error():
            """Log client-side errors."""
            data = self.get_request_data()
            required_fields = ['error', 'stack_trace']
            
            error = self.validate_required_fields(data, required_fields)
            if error:
                return self.json_response({'error': error}, 400)
                
            self.logger.error(f"Client error: {data['error']}\nStack trace: {data['stack_trace']}")
            
            # Record error metric
            performance_monitor.record_metric(
                name="client_error",
                value=1.0,
                endpoint="client",
                context={
                    'error': data['error'],
                    'stack_trace': data['stack_trace']
                }
            )
            
            return self.json_response({
                'status': 'success',
                'timestamp': datetime.now()
            })
            
        @self.blueprint.route('/log-metric', methods=['POST'])
        @self.handle_errors
        @rate_limiter.rate_limit('default')
        def log_metric():
            """Log client-side performance metrics."""
            data = self.get_request_data()
            required_fields = ['metric_name', 'value']
            
            error = self.validate_required_fields(data, required_fields)
            if error:
                return self.json_response({'error': error}, 400)
                
            # Record client metric
            performance_monitor.record_metric(
                name=data['metric_name'],
                value=float(data['value']),
                endpoint="client",
                context=data.get('context', {})
            )
            
            return self.json_response({
                'status': 'success',
                'timestamp': datetime.now()
            })
            
        @self.blueprint.route('/performance-report')
        @self.handle_errors
        @rate_limiter.rate_limit('status')
        @cache_service.cached(ttl=60)  # Cache for 1 minute
        def get_performance_report():
            """Get performance report."""
            perf_stats = performance_monitor.get_performance_report()
            cache_stats = cache_service.get_stats()
            rate_limits = rate_limiter.get_limits()
            rate_states = {
                key: rate_limiter.get_state(key)
                for key in rate_limits.keys()
            }
            
            return self.json_response({
                'status': 'success',
                'performance': perf_stats,
                'cache': cache_stats,
                'rate_limits': rate_limits,
                'rate_states': rate_states,
                'timestamp': datetime.now()
            }, compress=config_service.get('enable_compression', True))
            
        @self.blueprint.route('/clear-cache', methods=['POST'])
        @self.handle_errors
        @rate_limiter.rate_limit('default')
        def clear_cache():
            """Clear the API route cache."""
            cache_service.clear()
            return self.json_response({
                'status': 'success',
                'message': 'Cache cleared successfully',
                'timestamp': datetime.now()
            })
            
# Create the API route instance
api_route = APIRoute()

# Non-API routes that still belong in this blueprint
api_views_bp = Blueprint('api_views', __name__)

@api_views_bp.route("/api-status")
@api_route.handle_errors
@rate_limiter.rate_limit('status')
def api_status_view():
    """View for API status dashboard."""
    # Include navigation for the template
    nav_context = get_context_for_template()
    
    # Get API status and performance data
    status = get_metrics()
    perf_stats = performance_monitor.get_performance_report()
    cache_stats = cache_service.get_stats()
    rate_limits = rate_limiter.get_limits()
    rate_states = {
        key: rate_limiter.get_state(key)
        for key in rate_limits.keys()
    }
    
    return render_template(
        "finchat_dark_dashboard.html", 
        page_title="API Status Dashboard",
        template_type="api-status",
        api_status=status,
        performance=perf_stats,
        cache=cache_stats,
        rate_limits=rate_limits,
        rate_states=rate_states,
        **nav_context
    )

@api_views_bp.route("/debug")
@api_route.handle_errors
@rate_limiter.rate_limit('status')
def debug_info():
    """Debug endpoint for checking app status and configuration."""
    # Include navigation for the template
    nav_context = get_context_for_template()
    
    # Get performance and cache statistics
    perf_stats = performance_monitor.get_performance_report()
    cache_stats = cache_service.get_stats()
    rate_limits = rate_limiter.get_limits()
    rate_states = {
        key: rate_limiter.get_state(key)
        for key in rate_limits.keys()
    }
    config = config_service.to_dict()
    
    return render_template(
        "finchat_dark_dashboard.html", 
        page_title="Debug Information",
        template_type="debug",
        app_routes=[r.endpoint for r in request.app.url_map.iter_rules()],
        performance=perf_stats,
        cache=cache_stats,
        rate_limits=rate_limits,
        rate_states=rate_states,
        config=config,
        **nav_context
    )