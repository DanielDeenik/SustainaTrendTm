"""
Route blueprints for SustainaTrend Intelligence Platform
"""

import logging

def register_blueprints(app):
    """
    Register all blueprints with the Flask application
    
    Args:
        app: Flask application
    """
    logger = logging.getLogger(__name__)
    logger.info("Registering blueprints")
    
    # Import blueprints
    from .analytics import analytics_bp
    from .trend import trend_bp
    # Import the real estate blueprint
    import sys
    import os
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from realestate_sustainability import realestate_bp
    
    # Register blueprints
    app.register_blueprint(analytics_bp)
    app.register_blueprint(trend_bp)
    app.register_blueprint(realestate_bp)
    
    logger.info("All blueprints registered successfully")