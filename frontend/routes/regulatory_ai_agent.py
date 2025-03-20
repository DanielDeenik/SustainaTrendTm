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
    try:
        # Use relative or absolute path depending on the project structure
        try:
            from ..regulatory_ai_agent import register_routes
            logger.info("Imported regulatory_ai_agent from relative path")
        except ImportError:
            import sys
            from pathlib import Path
            
            # Add the parent directory to sys.path to allow importing
            sys.path.append(str(Path(__file__).parent.parent))
            
            from regulatory_ai_agent import register_routes
            logger.info("Imported regulatory_ai_agent from absolute path")
    except ImportError as e:
        logger.warning(f"Failed to import regulatory_ai_agent: {str(e)}")
        # Define a simple no-op function as fallback
        def register_routes(app):
            logger.warning("Using fallback empty register_routes for regulatory_ai_agent")
            pass
    
    # Register the routes with the app
    register_routes(app)
    
    # Also register the blueprint for any additional routes
    app.register_blueprint(regulatory_ai_bp)
    
    logger.info("Regulatory AI Agent blueprint registered successfully")
    return app