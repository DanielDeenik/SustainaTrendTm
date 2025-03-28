"""
Regulatory AI Agent Blueprint for SustainaTrend™

This blueprint registers the routes for the Regulatory AI Agent module, which
provides AI-powered assessment and assurance for regulatory compliance.

This module uses the shared regulatory AI services for improved maintenance.
"""

import logging
from flask import Blueprint
import importlib.util
import os
import sys

# Set up logging
logger = logging.getLogger(__name__)

# Import the main regulatory_ai_agent.py module to get the bp with all routes
try:
    # Try different import approaches to handle different execution contexts
    try:
        # First try standard import
        from frontend.regulatory_ai_agent import regulatory_ai_bp
        logger.info("Imported regulatory_ai_agent via regular import")
    except ImportError:
        # Try a different approach to import the module
        module_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'regulatory_ai_agent.py')
        if not os.path.exists(module_path):
            logger.error(f"Could not find regulatory_ai_agent.py at {module_path}")
            # Create empty blueprint as fallback
            regulatory_ai_bp = Blueprint('regulatory_ai', __name__, url_prefix='/regulatory-ai')
        else:
            spec = importlib.util.spec_from_file_location("regulatory_ai_agent", module_path)
            reg_ai_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(reg_ai_module)
            regulatory_ai_bp = reg_ai_module.regulatory_ai_bp
            logger.info(f"Imported regulatory_ai_agent via spec loader from {module_path}")
except Exception as e:
    logger.error(f"Error importing regulatory_ai_agent: {str(e)}")
    # Create empty blueprint as fallback
    regulatory_ai_bp = Blueprint('regulatory_ai', __name__, url_prefix='/regulatory-ai')

def register_blueprint(app):
    """
    Register the Regulatory AI Agent blueprint with the Flask application
    
    Args:
        app: Flask application
    """
    # Register the blueprint with all its routes
    app.register_blueprint(regulatory_ai_bp)
    
    logger.info(f"Regulatory AI Agent blueprint registered successfully (routes will be shown in the app's URL map)")
    
    return app