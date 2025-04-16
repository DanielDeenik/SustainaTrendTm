"""
API routes for the SustainaTrend™ Platform.
"""
from flask import Blueprint, jsonify, request, current_app
import logging
from datetime import datetime
import json
from src.frontend.refactored.services.mongodb_service import MongoDBService

# Configure logger
logger = logging.getLogger(__name__)

# Create blueprint
api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/health')
def health_check():
    """Check the health of the application and MongoDB connection."""
    try:
        mongodb = current_app.mongodb
        is_connected = mongodb.is_connected()
        return jsonify({
            'status': 'healthy' if is_connected else 'degraded',
            'mongodb': 'connected' if is_connected else 'disconnected'
        })
    except Exception as e:
        current_app.logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500

@api_bp.route('/metrics')
def get_metrics():
    """Get key metrics from different collections."""
    try:
        mongodb = current_app.mongodb
        metrics = {
            'trends': mongodb.get_metrics('trends'),
            'stories': mongodb.get_metrics('stories'),
            'portfolio': mongodb.get_metrics('portfolio')
        }
        return jsonify(metrics)
    except Exception as e:
        current_app.logger.error(f"Error fetching metrics: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@api_bp.route('/trends/categories')
def get_trend_categories():
    """Get trending categories."""
    try:
        mongodb = current_app.mongodb
        categories = mongodb.get_trending_categories()
        return jsonify({'categories': categories})
    except Exception as e:
        current_app.logger.error(f"Error fetching trend categories: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@api_bp.route('/portfolio/companies')
def get_portfolio_companies():
    """Get portfolio companies with optional filtering."""
    try:
        mongodb = current_app.mongodb
        sector = request.args.get('sector')
        companies = mongodb.get_portfolio_companies(sector=sector)
        return jsonify({'companies': companies})
    except Exception as e:
        current_app.logger.error(f"Error fetching portfolio companies: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@api_bp.route('/stories/recent')
def get_recent_stories():
    """Get recent stories with optional limit."""
    try:
        mongodb = current_app.mongodb
        limit = request.args.get('limit', default=5, type=int)
        stories = mongodb.get_stories(limit=limit)
        return jsonify({'stories': stories})
    except Exception as e:
        current_app.logger.error(f"Error fetching recent stories: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@api_bp.route('/strategies')
def get_strategies():
    """Get monetization strategies."""
    try:
        # Mock data for demonstration
        strategies = [
            {
                'name': 'Carbon Credits',
                'potential_revenue': 500000,
                'implementation_cost': 100000,
                'roi': 400
            },
            {
                'name': 'Sustainable Products',
                'potential_revenue': 1000000,
                'implementation_cost': 200000,
                'roi': 400
            }
        ]
        return jsonify(strategies)
    except Exception as e:
        logger.error(f"Error getting strategies: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/companies')
def get_companies():
    """Get company data."""
    try:
        # Mock data for demonstration
        companies = [
            {
                'name': 'EcoTech Solutions',
                'sustainability_score': 85,
                'industry': 'Technology',
                'location': 'Amsterdam'
            },
            {
                'name': 'GreenEnergy Corp',
                'sustainability_score': 92,
                'industry': 'Energy',
                'location': 'Berlin'
            }
        ]
        return jsonify(companies)
    except Exception as e:
        logger.error(f"Error getting companies: {str(e)}")
        return jsonify({'error': str(e)}), 500 