"""
Dashboard blueprint for SustainaTrend Intelligence Platform 2025
"""

import logging
from flask import Blueprint, render_template, jsonify

# Create blueprint
dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')
logger = logging.getLogger(__name__)

@dashboard_bp.route('/')
def dashboard():
    """Render the dashboard page"""
    logger.info("Dashboard route called")
    
    # Example metrics data - in a real app, this would come from a database
    metrics = {
        'carbon_emissions': {
            'value': 78.5,
            'unit': 'tonnes CO₂e',
            'change': -12.3
        },
        'energy_consumption': {
            'value': 342,
            'unit': 'MWh',
            'change': -8.7
        },
        'water_usage': {
            'value': 1.28,
            'unit': 'million L',
            'change': -4.2
        },
        'waste_generated': {
            'value': 56.3,
            'unit': 'tonnes',
            'change': -15.8
        }
    }
    
    # Performance targets
    targets = {
        'carbon_neutrality': {
            'value': 68,
            'target': '2030'
        },
        'renewable_energy': {
            'value': 42,
            'target': '100%'
        },
        'zero_waste': {
            'value': 35,
            'target': '2035'
        }
    }
    
    # Insights
    insights = [
        {
            'title': 'Carbon Reduction',
            'text': 'Your carbon emissions have decreased by 12.3% compared to last quarter. This puts you on track to meet your 2030 carbon neutrality goal.',
            'icon': 'lightbulb',
            'type': 'positive'
        },
        {
            'title': 'Water Usage Alert',
            'text': 'Water consumption is trending 5% above your quarterly target. Consider implementing the water conservation measures outlined in your sustainability plan.',
            'icon': 'exclamation-triangle',
            'type': 'warning'
        },
        {
            'title': 'Waste Management',
            'text': 'Your waste reduction initiatives have resulted in a 15.8% decrease in total waste. This exceeds your annual target of 10%.',
            'icon': 'check-circle',
            'type': 'positive'
        }
    ]
    
    return render_template('dashboard.html', 
                          active_nav='dashboard', 
                          metrics=metrics,
                          targets=targets,
                          insights=insights)

@dashboard_bp.route('/api/metrics')
def get_metrics():
    """API endpoint to get all metrics for the dashboard"""
    # Example metrics data - in a real app, this would come from a database
    metrics = {
        'emissions': {
            'current': 78.5,
            'previous': 89.5,
            'unit': 'tonnes CO₂e',
            'change_percentage': -12.3,
            'target': 0,
            'target_year': 2030,
            'scope_1': {
                'current': 25,
                'previous': 42,
                'monthly': [42, 40, 38, 37, 36, 35, 33, 31, 30, 28, 26, 25]
            },
            'scope_2': {
                'current': 42,
                'previous': 65,
                'monthly': [65, 63, 60, 58, 55, 52, 50, 49, 47, 45, 44, 42]
            },
            'scope_3': {
                'current': 93,
                'previous': 120,
                'monthly': [120, 118, 115, 112, 110, 108, 105, 103, 100, 98, 95, 93]
            }
        },
        'energy': {
            'total': {
                'current': 342,
                'previous': 374,
                'unit': 'MWh',
                'change_percentage': -8.7
            },
            'renewable': {
                'current': 143.64,
                'percentage': 42,
                'target': 100,
                'target_year': 2030
            }
        },
        'water': {
            'current': 1.28,
            'previous': 1.33,
            'unit': 'million L',
            'change_percentage': -4.2,
            'monthly': [1.4, 1.39, 1.37, 1.36, 1.35, 1.34, 1.33, 1.32, 1.31, 1.30, 1.29, 1.28]
        },
        'waste': {
            'current': 56.3,
            'previous': 66.9,
            'unit': 'tonnes',
            'change_percentage': -15.8,
            'target': 0,
            'target_year': 2035,
            'progress': 35
        },
        'esg_scores': {
            'environmental': {
                'current': 85,
                'industry_avg': 65
            },
            'social': {
                'current': 72,
                'industry_avg': 68
            },
            'governance': {
                'current': 78,
                'industry_avg': 72
            },
            'climate_risk': {
                'current': 65,
                'industry_avg': 58
            },
            'resource_use': {
                'current': 81,
                'industry_avg': 63
            },
            'human_capital': {
                'current': 76,
                'industry_avg': 70
            }
        }
    }
    
    return jsonify(metrics)

def register_blueprint(app):
    """Register blueprint with the Flask application"""
    app.register_blueprint(dashboard_bp)
    logger.info("Dashboard blueprint registered successfully")