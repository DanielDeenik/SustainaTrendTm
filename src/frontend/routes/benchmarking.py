"""
Benchmarking routes for SustainaTrend Intelligence Platform
"""

import logging
from flask import Blueprint, render_template, request, jsonify

# Create blueprint
benchmarking_bp = Blueprint('benchmarking', __name__)

# Configure logging
logger = logging.getLogger(__name__)

@benchmarking_bp.route('/')
def benchmarking():
    """Benchmarking dashboard page"""
    logger.info("Benchmarking route called")
    return render_template(
        'benchmarking.html',
        page_title="Benchmarking Dashboard"
    )

@benchmarking_bp.route('/api/data')
def get_benchmarking_data():
    """API endpoint to get benchmarking data"""
    # This would connect to real data in production
    data = {
        "industry_averages": {
            "carbon": 45.2,
            "energy": 38.7,
            "water": 42.1,
            "waste": 35.8
        },
        "peer_comparison": [
            {
                "name": "Company A",
                "score": 78.5,
                "metrics": {
                    "carbon": 82,
                    "energy": 75,
                    "water": 79,
                    "waste": 78
                }
            },
            {
                "name": "Company B",
                "score": 65.2,
                "metrics": {
                    "carbon": 68,
                    "energy": 62,
                    "water": 66,
                    "waste": 65
                }
            },
            {
                "name": "Company C",
                "score": 72.8,
                "metrics": {
                    "carbon": 75,
                    "energy": 70,
                    "water": 73,
                    "waste": 73
                }
            }
        ]
    }
    return jsonify(data)