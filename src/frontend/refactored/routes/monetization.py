"""
Monetization routes for the SustainaTrend™ Platform.
"""
from flask import Blueprint, render_template, jsonify, request
from src.frontend.refactored.services.mongodb_service import mongodb_service
import logging

monetization_bp = Blueprint('monetization', __name__, url_prefix='/monetization')

@monetization_bp.route('/')
def index():
    """Render the Monetization dashboard."""
    try:
        return render_template('monetization/index.html')
    except Exception as e:
        logging.error(f"Error rendering Monetization dashboard: {str(e)}")
        return render_template('errors/500.html'), 500

@monetization_bp.route('/api/revenue')
def get_revenue():
    """Get revenue data."""
    try:
        if not mongodb_service.is_connected():
            return jsonify({'error': 'Database not connected'}), 503
        revenue = mongodb_service.find('monetization.revenue', {})
        return jsonify(revenue)
    except Exception as e:
        logging.error(f"Error fetching revenue data: {str(e)}")
        return jsonify({'error': 'Failed to fetch revenue data'}), 500

@monetization_bp.route('/api/metrics')
def get_metrics():
    """Get monetization metrics."""
    try:
        if not mongodb_service.is_connected():
            return jsonify({'error': 'Database not connected'}), 503
        metrics = mongodb_service.find('monetization.metrics', {})
        return jsonify(metrics)
    except Exception as e:
        logging.error(f"Error fetching monetization metrics: {str(e)}")
        return jsonify({'error': 'Failed to fetch metrics'}), 500 