"""
Overview dashboard blueprint for SustainaTrend Intelligence Platform
"""
import logging
logger = logging.getLogger(__name__)

from flask import Blueprint, render_template, jsonify

# Create blueprint
overview_bp = Blueprint('overview', __name__, url_prefix='/overview')

@overview_bp.route('/')
def overview():
    """Render the company overview page"""
    logger.info("Overview route called")
    return render_template(
        'overview.html',
        active_nav='overview',
        page_title='Company Overview'
    )

@overview_bp.route('/api/summary')
def get_overview_data():
    """API endpoint to get company overview data"""
    # This would connect to real data in production
    data = {
        "company": {
            "name": "Example Corporation",
            "industry": "Technology",
            "founded": 2005,
            "employees": 1250,
            "locations": ["New York", "London", "Singapore"]
        },
        "sustainability_summary": {
            "esg_rating": "AA",
            "emission_reduction": "28%",
            "renewable_energy": "42%",
            "waste_reduction": "35%",
            "water_conservation": "22%"
        },
        "key_initiatives": [
            {"name": "Carbon Neutral Operations", "status": "In Progress", "completion": 65},
            {"name": "Zero Waste Campus", "status": "In Progress", "completion": 48},
            {"name": "Renewable Energy Transition", "status": "On Track", "completion": 42},
            {"name": "Sustainable Supply Chain", "status": "Planning", "completion": 25}
        ]
    }
    return jsonify(data)

def register_blueprint(app):
    """Register blueprint with the Flask application"""
    app.register_blueprint(overview_bp)
    logger.info("Overview blueprint registered successfully")