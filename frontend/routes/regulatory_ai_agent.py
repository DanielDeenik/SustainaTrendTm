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
regulatory_ai_bp = Blueprint('regulatory_ai_routes', __name__)

def register_blueprint(app):
    """
    Register the Regulatory AI Agent blueprint with the Flask application
    
    Args:
        app: Flask application
    """
    # Import the module to register its routes
    from frontend.regulatory_ai_agent import register_routes
    
    # Register the routes with the app
    register_routes(app)
    
    # Also register the blueprint for any additional routes
    app.register_blueprint(regulatory_ai_bp)
    
    logger.info("Regulatory AI Agent blueprint registered successfully")
    return app