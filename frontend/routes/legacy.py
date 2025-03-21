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

# Route for legacy storytelling page
@legacy_bp.route('/storytelling')
def storytelling_redirect():
    """
    Redirects from the legacy /storytelling route 
    to the new modular stories blueprint
    """
    logger.info("Legacy storytelling route accessed - redirecting to stories blueprint")
    return redirect(url_for('stories.stories_home'))

# Route for legacy story creation page
@legacy_bp.route('/storytelling/create')
def storytelling_create_redirect():
    """
    Redirects from the legacy /storytelling/create route 
    to the new modular stories create page
    """
    from flask import request
    logger.info("Legacy storytelling create route accessed - redirecting to stories create page")
    
    # Check if template parameter is present and carry it over to the new URL
    template_param = request.args.get('template')
    if template_param:
        return redirect(url_for('stories.create_story', template=template_param))
    else:
        return redirect(url_for('stories.create_story'))

# Route for legacy sustainability stories page
@legacy_bp.route('/sustainability-stories')
def sustainability_stories_redirect():
    """
    Redirects from the legacy /sustainability-stories route 
    to the new modular storytelling blueprint
    """
    logger.info("Legacy sustainability stories route accessed - redirecting to new blueprint")
    return redirect(url_for('stories.stories_home'))

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
    to the enhanced strategy hub
    """
    logger.info("Legacy monetization opportunities route accessed - redirecting to enhanced strategy hub")
    return redirect(url_for('enhanced_strategy.enhanced_strategy_hub'))

# Route for legacy trend virality dashboard
@legacy_bp.route('/trend-virality-dashboard')
def trend_virality_redirect():
    """
    Redirects from the legacy /trend-virality-dashboard route
    to the enhanced strategy hub's virality trends tab
    """
    logger.info("Legacy trend virality dashboard route accessed - redirecting to enhanced strategy hub with virality tab")
    return redirect(url_for('enhanced_strategy.enhanced_strategy_hub') + '#virality-trends')

# Function to register blueprint
def register_blueprint(app):
    """
    Register legacy routes with the application
    
    Args:
        app: Flask application
    """
    app.register_blueprint(legacy_bp)
    logger.info("Legacy routes blueprint registered successfully")

# Alias for backward compatibility
register_legacy_routes = register_blueprint