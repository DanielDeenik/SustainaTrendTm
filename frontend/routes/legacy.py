"""
Legacy Routes Blueprint for SustainaTrend™ Intelligence Platform

This module provides redirects from old routes to the new blueprint-based routes
to maintain backward compatibility while migrating to a more modular structure.
"""
import logging
from flask import Blueprint, redirect, url_for

# Configure logging
logger = logging.getLogger(__name__)

# Create legacy routes blueprint (no URL prefix to handle legacy paths directly)
legacy_bp = Blueprint('legacy', __name__)

# Route for legacy sustainability stories page
@legacy_bp.route('/sustainability-stories')
def sustainability_stories_redirect():
    """
    Redirects from the legacy /sustainability-stories route 
    to the new modular storytelling blueprint
    """
    logger.info("Legacy sustainability stories route accessed - redirecting to new blueprint")
    return redirect(url_for('storytelling.storytelling_home'))

# Route for legacy analytics
@legacy_bp.route('/analytics')
def analytics_redirect():
    """
    Redirects from the legacy /analytics route
    to the new analytics blueprint
    """
    logger.info("Legacy analytics route accessed - redirecting to new blueprint")
    return redirect(url_for('analytics.dashboard'))

# Route for legacy monetization
@legacy_bp.route('/monetization-opportunities')
def monetization_redirect():
    """
    Redirects from the legacy /monetization-opportunities route
    to the new monetization routes
    """
    logger.info("Legacy monetization opportunities route accessed - redirecting to new blueprint")
    return redirect(url_for('strategy.strategy_hub_monetization'))

# Function to register blueprint
def register_legacy_routes(app):
    """
    Register legacy routes with the application
    
    Args:
        app: Flask application
    """
    app.register_blueprint(legacy_bp)
    logger.info("Legacy routes blueprint registered successfully")