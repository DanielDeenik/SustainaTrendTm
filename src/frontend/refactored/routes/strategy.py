"""
Strategy routes for the SustainaTrend™ Platform.
"""
from flask import Blueprint, render_template, jsonify, request
from src.frontend.refactored.services.mongodb_service import mongodb_service
import logging

strategy_bp = Blueprint('strategy', __name__, url_prefix='/strategy')

@strategy_bp.route('/')
def index():
    """Render the Strategy Hub dashboard."""
    try:
        return render_template('strategy/index.html')
    except Exception as e:
        logging.error(f"Error rendering Strategy Hub: {str(e)}")
        return render_template('errors/500.html'), 500

@strategy_bp.route('/api/insights')
def get_insights():
    """Get strategy insights data."""
    try:
        if not mongodb_service.is_connected():
            return jsonify({'error': 'Database not connected'}), 503
        insights = mongodb_service.find('strategy.insights', {})
        return jsonify(insights)
    except Exception as e:
        logging.error(f"Error fetching strategy insights: {str(e)}")
        return jsonify({'error': 'Failed to fetch insights'}), 500

@strategy_bp.route('/api/models')
def get_models():
    """Get strategy models data."""
    try:
        if not mongodb_service.is_connected():
            return jsonify({'error': 'Database not connected'}), 503
        models = mongodb_service.find('strategy.models', {})
        return jsonify(models)
    except Exception as e:
        logging.error(f"Error fetching strategy models: {str(e)}")
        return jsonify({'error': 'Failed to fetch models'}), 500 