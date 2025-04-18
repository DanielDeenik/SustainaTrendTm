"""
Real Estate routes for the SustainaTrend™ Platform.
"""
from flask import Blueprint, render_template, jsonify, request
from src.frontend.refactored.services.mongodb_service import mongodb_service
import logging

# Configure logger
logger = logging.getLogger(__name__)

realestate_bp = Blueprint('realestate', __name__, url_prefix='/real-estate')

@realestate_bp.route('/')
def index():
    """Render the Real Estate dashboard."""
    try:
        # Get recent properties for the dashboard
        properties = mongodb_service.find('properties', limit=5)
        metrics = mongodb_service.get_metrics(limit=5)
        
        return render_template('realestate/index.html', 
                             properties=properties,
                             metrics=metrics)
    except Exception as e:
        logger.error(f"Error rendering Real Estate dashboard: {str(e)}")
        return render_template('errors/500.html'), 500

@realestate_bp.route('/api/properties')
def get_properties():
    """Get real estate properties data."""
    try:
        if not mongodb_service.is_connected():
            return jsonify({'error': 'Database connection not available'}), 503
            
        properties = mongodb_service.find('properties')
        return jsonify({
            'status': 'success',
            'data': properties
        })
    except Exception as e:
        logger.error(f"Error fetching properties: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to fetch properties'
        }), 500

@realestate_bp.route('/api/properties/<property_id>')
def get_property(property_id):
    """Get details for a specific property."""
    try:
        if not mongodb_service.is_connected():
            return jsonify({'error': 'Database connection not available'}), 503
            
        property_data = mongodb_service.find('properties', 
                                           query={'property_id': property_id})
        if not property_data:
            return jsonify({
                'status': 'error',
                'message': 'Property not found'
            }), 404
            
        metrics = mongodb_service.get_metrics(property_id=property_id)
        
        return jsonify({
            'status': 'success',
            'data': {
                'property': property_data[0],
                'metrics': metrics
            }
        })
    except Exception as e:
        logger.error(f"Error fetching property {property_id}: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to fetch property details'
        }), 500 