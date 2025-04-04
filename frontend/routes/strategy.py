"""
Strategy Hub routes for SustainaTrend Intelligence Platform

This module provides consistent redirect support for various strategy-related URLs
to the main strategy hub at /strategy-hub/ for a simplified user experience.
"""

import logging
from flask import Blueprint, redirect, url_for, Flask

# Create blueprint
strategy_bp = Blueprint('strategy', __name__, url_prefix='/strategy')
strategy_hub_bp = Blueprint('strategy_hub', __name__, url_prefix='/strategy-hub-legacy')
logger = logging.getLogger(__name__)

logger.info("Strategy blueprint initialized (redirect mode)")

# Simple redirects for all legacy routes
@strategy_bp.route('/', defaults={'path': ''})
@strategy_bp.route('/<path:path>')
def redirect_to_main_strategy_hub(path):
    """Redirect all /strategy/* routes to main strategy hub"""
    logger.info(f"Redirecting /strategy/{path} to main strategy hub")
    return redirect('/strategy-hub/')

# Register the blueprint with the app
def register_blueprint(app):
    """Register the strategy blueprint with Flask app"""
    app.register_blueprint(strategy_bp)
    logger.info("Strategy redirect blueprint registered")