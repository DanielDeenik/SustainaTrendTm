"""
Enhanced Strategy Hub blueprint for SustainaTrend Intelligence Platform 2025 Refresh

Centralized implementation with Finchat.io-style UI and on-demand elements.
This is now the main strategy interface for the platform.
"""

import logging

# Create a logger
logger = logging.getLogger(__name__)

# Import the strategy blueprint from enhanced_strategy_routes and rename it for export
from ..enhanced_strategy_routes import strategy_bp as enhanced_strategy_bp

def register_blueprint(app):
    """
    Register the Enhanced Strategy Hub blueprint and route handlers
    
    Args:
        app: Flask application
    """
    try:
        app.register_blueprint(enhanced_strategy_bp)
        logger.info("Enhanced Strategy Hub blueprint registered successfully")
    except Exception as e:
        logger.error(f"Error registering Enhanced Strategy Hub blueprint: {e}")
        raise