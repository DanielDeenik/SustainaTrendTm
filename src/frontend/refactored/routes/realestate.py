"""
Real Estate routes for the SustainaTrend™ Platform.
"""
from flask import Blueprint, render_template, jsonify, request
from src.frontend.refactored.services.mongodb_service import get_mongodb_service
import logging

realestate_bp = Blueprint('realestate', __name__, url_prefix='/real-estate')

@realestate_bp.route('/')
def index():
    """Render the Real Estate dashboard."""
    try:
        return render_template('realestate/index.html')
    except Exception as e:
        logging.error(f"Error rendering Real Estate dashboard: {str(e)}")
        return render_template('errors/500.html'), 500

@realestate_bp.route('/api/properties')
def get_properties():
    """Get real estate properties data."""
    try:
        db = get_mongodb_service()
        properties = list(db.real_estate.properties.find())
        return jsonify(properties)
    except Exception as e:
        logging.error(f"Error fetching properties: {str(e)}")
        return jsonify({'error': 'Failed to fetch properties'}), 500 