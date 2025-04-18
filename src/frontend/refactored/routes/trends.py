"""
Trend analysis routes for the SustainaTrend™ Platform.
"""
from flask import Blueprint, render_template, jsonify, request, current_app
import logging
from src.frontend.refactored.services.mongodb_service import mongodb_service

# Configure logger
logger = logging.getLogger(__name__)

trends_bp = Blueprint('trends', __name__, url_prefix='/trends')

@trends_bp.route('/')
def index():
    """Render the trends overview page."""
    try:
        # Use the singleton MongoDB service instance
        mongodb = mongodb_service
        recent_trends = mongodb.get_trends(limit=10)
        return render_template('trends/index.html', trends=recent_trends)
    except Exception as e:
        logger.error(f"Error fetching trends: {str(e)}")
        return render_template('errors/500.html'), 500

@trends_bp.route('/analysis/<trend_id>')
def analysis(trend_id):
    """Render the detailed trend analysis page."""
    try:
        # Use the singleton MongoDB service instance
        mongodb = mongodb_service
        trend = mongodb.get_trend_by_id(trend_id)
        if not trend:
            return render_template('errors/404.html'), 404
            
        metrics = mongodb.get_trend_metrics(trend_id)
        return render_template('trends/analysis.html', trend=trend, metrics=metrics)
    except Exception as e:
        logger.error(f"Error analyzing trend {trend_id}: {str(e)}")
        return render_template('errors/500.html'), 500

@trends_bp.route('/api/trends')
def get_trends():
    """API endpoint to get trends data."""
    try:
        # Use the singleton MongoDB service instance
        mongodb = mongodb_service
        limit = request.args.get('limit', default=10, type=int)
        category = request.args.get('category')
        
        if category:
            trends = mongodb.get_trends(category=category, limit=limit)
        else:
            trends = mongodb.get_trends(limit=limit)
            
        return jsonify({'trends': trends})
    except Exception as e:
        logger.error(f"Error fetching trends API: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500 