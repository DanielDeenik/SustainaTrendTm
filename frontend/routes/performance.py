"""
Performance metrics blueprint for SustainaTrend Intelligence Platform
"""
import logging
logger = logging.getLogger(__name__)

from flask import Blueprint, render_template, jsonify

# Create blueprint
performance_bp = Blueprint('performance', __name__, url_prefix='/performance')

@performance_bp.route('/')
def performance():
    """Redirect to dashboard (performance.html has been removed)"""
    from flask import redirect
    logger.info("Performance metrics route redirecting to dashboard")
    return redirect('/dashboard/')

@performance_bp.route('/api/data')
def get_performance_data():
    """API endpoint to get performance metrics data"""
    # This would connect to real metrics in production
    metrics = [
        {"id": 1, "name": "Carbon Emissions", "value": 125.3, "unit": "tons", "target": 100, "change": -12.3},
        {"id": 2, "name": "Energy Usage", "value": 1450, "unit": "MWh", "target": 1200, "change": -5.2},
        {"id": 3, "name": "Water Consumption", "value": 22500, "unit": "m³", "target": 20000, "change": -8.7},
        {"id": 4, "name": "Waste Generated", "value": 87.5, "unit": "tons", "target": 75, "change": -15.1},
        {"id": 5, "name": "Renewable Energy", "value": 42.8, "unit": "%", "target": 60, "change": 8.3},
    ]
    return jsonify(metrics)

def register_blueprint(app):
    """Register blueprint with the Flask application"""
    app.register_blueprint(performance_bp)
    logger.info("Performance metrics blueprint registered successfully")