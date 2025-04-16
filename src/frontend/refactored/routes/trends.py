"""
Trend analysis routes for the SustainaTrend™ Platform.
"""
from flask import Blueprint, render_template, jsonify, request, current_app
from src.frontend.refactored.services.mongodb_service import MongoDBService

trends_bp = Blueprint('trends', __name__, url_prefix='/trends')

@trends_bp.route('/')
def index():
    """Render the trends overview page."""
    try:
        mongodb = current_app.mongodb
        recent_trends = mongodb.get_trends(limit=10)
        return render_template('trends/index.html', trends=recent_trends)
    except Exception as e:
        current_app.logger.error(f"Error fetching trends: {str(e)}")
        return render_template('errors/500.html'), 500

@trends_bp.route('/analysis/<trend_id>')
def analysis(trend_id):
    """Render the detailed trend analysis page."""
    try:
        mongodb = current_app.mongodb
        trend = mongodb.get_trend(trend_id)
        if not trend:
            return render_template('errors/404.html'), 404
            
        metrics = mongodb.get_metrics_by_category(trend.get('category'))
        return render_template('trends/analysis.html', trend=trend, metrics=metrics)
    except Exception as e:
        current_app.logger.error(f"Error analyzing trend {trend_id}: {str(e)}")
        return render_template('errors/500.html'), 500

@trends_bp.route('/api/trends')
def get_trends():
    """API endpoint to get trends data."""
    try:
        mongodb = current_app.mongodb
        limit = request.args.get('limit', default=10, type=int)
        category = request.args.get('category')
        
        if category:
            trends = mongodb.get_trends_by_category(category, limit=limit)
        else:
            trends = mongodb.get_trends(limit=limit)
            
        return jsonify({'trends': trends})
    except Exception as e:
        current_app.logger.error(f"Error fetching trends API: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500 