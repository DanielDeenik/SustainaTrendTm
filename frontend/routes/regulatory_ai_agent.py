"""
Regulatory AI Agent Blueprint for SustainaTrend™

This blueprint registers the routes for the Regulatory AI Agent module, which
provides AI-powered assessment and assurance for regulatory compliance.
"""

import logging
from flask import Blueprint

# Set up logging
logger = logging.getLogger(__name__)

# Create blueprint
regulatory_ai_bp = Blueprint('regulatory_ai_routes', __name__, url_prefix='/regulatory-ai')

def register_blueprint(app):
    """
    Register the Regulatory AI Agent blueprint with the Flask application
    
    Args:
        app: Flask application
    """
    # NOTE: We're no longer importing register_routes from regulatory_ai_agent.py 
    # to avoid duplicate route registration. We're only registering the blueprint itself.
    
    # Register the blueprint for regulatory AI routes
    app.register_blueprint(regulatory_ai_bp)
    
    logger.info("Regulatory AI Agent blueprint registered successfully")
    return app