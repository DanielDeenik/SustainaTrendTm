"""
Admin routes for system monitoring and management.
"""
from flask import Blueprint, render_template, jsonify, request, current_app
from functools import wraps
import logging
import psutil
import os
from datetime import datetime
from src.frontend.refactored.services.mongodb_service import MongoDBService

# Configure logger
logger = logging.getLogger(__name__)

# Create blueprint
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not request.headers.get('X-Admin-Key') == os.getenv('ADMIN_KEY'):
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    """Admin dashboard showing system metrics and status."""
    try:
        # System metrics
        cpu_percent = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # MongoDB connection status
        mongo_status = "Connected" if MongoDBService.is_connected() else "Disconnected"
        
        # API endpoints status
        api_status = {
            'health': check_endpoint_health('/api/health'),
            'metrics': check_endpoint_health('/api/metrics'),
            'trends': check_endpoint_health('/api/trends'),
            'stories': check_endpoint_health('/api/stories'),
            'strategies': check_endpoint_health('/api/strategies'),
            'companies': check_endpoint_health('/api/companies')
        }
        
        return render_template('admin/dashboard.html',
                             cpu_percent=cpu_percent,
                             memory_percent=memory.percent,
                             disk_percent=disk.percent,
                             mongo_status=mongo_status,
                             api_status=api_status)
    except Exception as e:
        logger.error(f"Error in admin dashboard: {str(e)}")
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/metrics')
@admin_required
def metrics():
    """Get detailed system metrics."""
    try:
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'system': {
                'cpu': {
                    'percent': psutil.cpu_percent(interval=1),
                    'count': psutil.cpu_count(),
                    'freq': psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None
                },
                'memory': psutil.virtual_memory()._asdict(),
                'disk': psutil.disk_usage('/')._asdict()
            },
            'mongodb': {
                'connected': MongoDBService.is_connected(),
                'collections': MongoDBService.get_collection_stats() if MongoDBService.is_connected() else None
            },
            'api': {
                'endpoints': get_api_metrics()
            }
        }
        return jsonify(metrics)
    except Exception as e:
        logger.error(f"Error getting metrics: {str(e)}")
        return jsonify({'error': str(e)}), 500

def check_endpoint_health(endpoint):
    """Check if an API endpoint is healthy."""
    try:
        response = current_app.test_client().get(endpoint)
        return {
            'status': 'healthy' if response.status_code == 200 else 'unhealthy',
            'status_code': response.status_code,
            'response_time': response.headers.get('X-Response-Time', 'N/A')
        }
    except Exception as e:
        logger.error(f"Error checking endpoint {endpoint}: {str(e)}")
        return {
            'status': 'error',
            'error': str(e)
        }

def get_api_metrics():
    """Get detailed API metrics."""
    endpoints = [
        '/api/health',
        '/api/metrics',
        '/api/trends',
        '/api/stories',
        '/api/strategies',
        '/api/companies'
    ]
    
    metrics = {}
    for endpoint in endpoints:
        metrics[endpoint] = check_endpoint_health(endpoint)
    
    return metrics 