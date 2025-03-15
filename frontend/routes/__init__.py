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
    
    # Import legacy routes blueprint - for backward compatibility
    try:
        from .legacy import legacy_bp
        logger.info("Legacy routes blueprint imported successfully")
    except ImportError:
        logger.warning("Legacy routes blueprint import failed, backward compatibility may be affected")
    
    # Import storytelling blueprint - new modular implementation
    try:
        from .storytelling import storytelling_bp
        logger.info("Storytelling blueprint imported successfully")
    except ImportError:
        logger.warning("Storytelling blueprint import failed, will rely on strategy hub")
    
    # Import the monetization blueprint but don't register it - we'll consolidate it into strategy
    try:
        from .monetization import monetization_bp
        logger.info("Monetization blueprint imported successfully")
    except ImportError:
        logger.warning("Monetization blueprint import failed, will rely on strategy hub")
        
    # Import science-based targets blueprint
    try:
        import sys
        from pathlib import Path
        
        # Add the parent directory to sys.path to allow importing science_based_targets
        sys.path.append(str(Path(__file__).parent.parent))
        
        from science_based_targets import sbti_bp
        logger.info("Science-Based Targets blueprint imported successfully")
    except ImportError as e:
        logger.warning(f"Science-Based Targets blueprint import failed: {str(e)}")
    
    # Register blueprints
    app.register_blueprint(analytics_bp)
    app.register_blueprint(trend_bp)
    app.register_blueprint(realestate_bp)
    # Register strategy blueprint - this contains the consolidated strategy hub
    app.register_blueprint(strategy_bp)
    # Register storytelling blueprint - modular implementation with UUID-based identification
    try:
        app.register_blueprint(storytelling_bp)
        logger.info("Storytelling blueprint registered successfully")
    except NameError:
        logger.warning("Storytelling blueprint not registered due to import failure")
    
    # Register legacy routes blueprint - must be last to avoid conflicts
    try:
        app.register_blueprint(legacy_bp)
        logger.info("Legacy routes blueprint registered successfully")
    except NameError:
        logger.warning("Legacy routes blueprint not registered due to import failure")
    
    # Register science-based targets blueprint
    try:
        app.register_blueprint(sbti_bp)
        logger.info("Science-Based Targets blueprint registered successfully")
    except NameError:
        logger.warning("Science-Based Targets blueprint not registered due to import failure")
    
    logger.info("All blueprints registered successfully")