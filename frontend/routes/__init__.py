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
    from .realestate import realestate_bp
    from .strategy import strategy_bp
    
    # Import the monetization blueprint but don't register it - we'll consolidate it into strategy
    try:
        from .monetization import monetization_bp
        logger.info("Monetization blueprint imported successfully")
    except ImportError:
        logger.warning("Monetization blueprint import failed, will rely on strategy hub")
    
    # Register blueprints
    app.register_blueprint(analytics_bp)
    app.register_blueprint(trend_bp)
    app.register_blueprint(realestate_bp)
    # Register strategy blueprint - this contains the consolidated strategy hub
    app.register_blueprint(strategy_bp)
    
    logger.info("All blueprints registered successfully")