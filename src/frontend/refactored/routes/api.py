"""
API routes for the SustainaTrend™ Platform.
"""
from flask import Blueprint, jsonify, request, current_app
import logging
from datetime import datetime
import json
from src.frontend.refactored.services.mongodb_service import mongodb_service

# Configure logger
logger = logging.getLogger(__name__)

# Create blueprint
api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/health')
def health_check():
    """Check the health of the application and MongoDB connection."""
    try:
        is_connected = mongodb_service.is_connected()
        return jsonify({
            'status': 'healthy' if is_connected else 'degraded',
            'mongodb_status': 'connected' if is_connected else 'disconnected',
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0',
            'environment': 'development'
        })
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500

@api_bp.route('/metrics')
def get_metrics():
    """Get key metrics from different collections."""
    try:
        metrics = {
            'trends': mongodb_service.find('trends', limit=5),
            'stories': mongodb_service.find('stories', limit=5),
            'portfolio': mongodb_service.find('portfolio_companies', limit=5)
        }
        return jsonify(metrics)
    except Exception as e:
        logger.error(f"Error fetching metrics: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/trends/categories')
def get_trend_categories():
    """Get trending categories."""
    try:
        trends = mongodb_service.find('trends', limit=10)
        categories = list(set(trend['category'] for trend in trends))
        return jsonify(categories)
    except Exception as e:
        logger.error(f"Error fetching trend categories: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/portfolio/companies')
def get_portfolio_companies():
    """Get portfolio companies."""
    try:
        companies = mongodb_service.find('portfolio_companies', limit=10)
        return jsonify(companies)
    except Exception as e:
        logger.error(f"Error fetching portfolio companies: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/stories/recent')
def get_recent_stories():
    """Get recent stories."""
    try:
        stories = mongodb_service.find('stories', limit=5)
        return jsonify(stories)
    except Exception as e:
        logger.error(f"Error fetching recent stories: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/strategies')
def get_strategies():
    """Get strategies."""
    try:
        strategies = mongodb_service.find('strategy.insights', limit=5)
        return jsonify(strategies)
    except Exception as e:
        logger.error(f"Error fetching strategies: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/companies')
def get_companies():
    """Get companies."""
    try:
        companies = mongodb_service.find('portfolio_companies', limit=10)
        return jsonify(companies)
    except Exception as e:
        logger.error(f"Error fetching companies: {str(e)}")
        return jsonify({'error': str(e)}), 500 