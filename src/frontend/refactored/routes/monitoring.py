"""
Monitoring routes for the SustainaTrend™ Intelligence Platform.
"""
import logging
from flask import Blueprint, jsonify, render_template
from src.frontend.refactored.services.monitoring_service import monitoring_service
from src.frontend.refactored.services.mongodb_service import mongodb_service

# Configure logger
logger = logging.getLogger(__name__)

# Create blueprint
monitoring_bp = Blueprint('monitoring', __name__, url_prefix='/monitoring')

@monitoring_bp.route('/')
def dashboard():
    """Render the monitoring dashboard."""
    try:
        return render_template('monitoring/dashboard.html')
    except Exception as e:
        logger.error(f"Error rendering monitoring dashboard: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Error rendering monitoring dashboard',
            'error': str(e)
        }), 500

@monitoring_bp.route('/api/health')
def health_check():
    """Get health status of all services."""
    try:
        # Get overall health status
        health_status = monitoring_service.get_health_status()
        
        # Get MongoDB status
        mongodb_status = monitoring_service.get_mongodb_status()
        
        # Get API status
        api_status = monitoring_service.get_api_status()
        
        # Get system metrics
        system_metrics = monitoring_service.get_system_metrics()
        
        return jsonify({
            'status': 'healthy',
            'health': health_status,
            'mongodb': mongodb_status,
            'api': api_status,
            'system': system_metrics
        })
    except Exception as e:
        logger.error(f"Error getting health status: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Error getting health status',
            'error': str(e)
        }), 500

@monitoring_bp.route('/api/metrics')
def get_metrics():
    """Get system metrics history."""
    try:
        metrics = monitoring_service.get_metrics_history()
        return jsonify({
            'status': 'success',
            'metrics': metrics
        })
    except Exception as e:
        logger.error(f"Error getting metrics: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Error getting metrics',
            'error': str(e)
        }), 500 