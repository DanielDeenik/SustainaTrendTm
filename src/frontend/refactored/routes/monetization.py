"""
Monetization routes for the SustainaTrend™ Platform.
"""
from flask import Blueprint, render_template, jsonify, request
from src.frontend.refactored.services.mongodb_service import get_mongodb_service
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
        db = get_mongodb_service()
        revenue = list(db.monetization.revenue.find())
        return jsonify(revenue)
    except Exception as e:
        logging.error(f"Error fetching revenue data: {str(e)}")
        return jsonify({'error': 'Failed to fetch revenue data'}), 500

@monetization_bp.route('/api/metrics')
def get_metrics():
    """Get monetization metrics."""
    try:
        db = get_mongodb_service()
        metrics = list(db.monetization.metrics.find())
        return jsonify(metrics)
    except Exception as e:
        logging.error(f"Error fetching monetization metrics: {str(e)}")
        return jsonify({'error': 'Failed to fetch metrics'}), 500 