"""
Regulatory AI Agent Blueprint for SustainaTrend™

This blueprint registers the routes for the Regulatory AI Agent module, which
provides AI-powered assessment and assurance for regulatory compliance.
"""

import logging
import os
import sys
from flask import Blueprint
from importlib import util

# Set up logging
logger = logging.getLogger(__name__)

# Import the refactored regulatory_ai_agent.py module
try:
    # Try importing the module using various approaches to handle different execution contexts
    try:
        # Standard import first
        from frontend.regulatory_ai_agent_refactored import regulatory_ai_bp
        logger.info("Imported refactored regulatory_ai_agent via regular import")
    except ImportError:
        # Try direct file import
        module_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'regulatory_ai_agent_refactored.py')
        if not os.path.exists(module_path):
            logger.error(f"Could not find regulatory_ai_agent_refactored.py at {module_path}")
            # Create empty blueprint as fallback
            regulatory_ai_bp = Blueprint('regulatory_ai', __name__, url_prefix='/regulatory-ai')
        else:
            spec = util.spec_from_file_location("regulatory_ai_agent_refactored", module_path)
            reg_ai_module = util.module_from_spec(spec)
            spec.loader.exec_module(reg_ai_module)
            regulatory_ai_bp = reg_ai_module.regulatory_ai_bp
            logger.info(f"Imported refactored regulatory_ai_agent via spec loader from {module_path}")
except Exception as e:
    logger.error(f"Error importing refactored regulatory_ai_agent: {str(e)}")
    # Create empty blueprint as fallback with a unique name
    regulatory_ai_bp = Blueprint('regulatory_ai_refactored', __name__, url_prefix='/regulatory-ai-refactored')

def register_blueprint(app):
    """
    Register the Regulatory AI Agent blueprint with the Flask application
    
    Args:
        app: Flask application
    """
    # Register the blueprint with all its routes
    app.register_blueprint(regulatory_ai_bp)
    logger.info("Refactored Regulatory AI Agent blueprint registered successfully")
    return app