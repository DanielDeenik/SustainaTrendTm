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
    
    # Import enhanced strategy blueprint - centralized implementation with Finchat.io-style UI
    # This is now the only strategy blueprint as all others have been consolidated into it
    try:
        from .enhanced_strategy import enhanced_strategy_bp, register_blueprint as register_enhanced_strategy
        logger.info("Enhanced Strategy Hub blueprint imported successfully")
    except ImportError as e:
        logger.error(f"Enhanced Strategy Hub blueprint import failed: {str(e)}")
        logger.error("This is a critical error as the Enhanced Strategy Hub is now the main strategy interface")
    
    # Import strategy redirect blueprint for backward compatibility
    try:
        from .strategy import strategy_bp, register_blueprint as register_strategy_redirect
        logger.info("Strategy redirect blueprint imported successfully")
    except ImportError as e:
        logger.warning(f"Strategy redirect blueprint import failed: {str(e)}")
    
    # Import storytelling blueprint - new modular implementation
    try:
        from .stories import stories_bp, register_blueprint as register_stories
        logger.info("Stories blueprint imported successfully")
    except ImportError as e:
        logger.warning(f"Stories blueprint import failed: {str(e)}. Will rely on enhanced strategy hub")
    
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
        
    # Regulatory AI functionality has been consolidated into the Data Moat blueprint
    # No separate regulatory AI blueprints are needed anymore
    logger.info("Regulatory AI functionality has been consolidated into Data Moat blueprint")
    
    # Import data moat blueprint
    try:
        from .data_moat_routes import data_moat_bp, register_routes as register_data_moat
        logger.info("Data Moat blueprint imported successfully")
    except ImportError as e:
        logger.warning(f"Data Moat blueprint import failed: {str(e)}")
        
    # Import document routes blueprint
    try:
        from .documents.document_routes import document_bp, register_routes as register_document_routes
        logger.info("Document routes blueprint imported successfully")
    except ImportError as e:
        logger.warning(f"Document routes blueprint import failed: {str(e)}")
    
    # Register blueprints
    app.register_blueprint(analytics_bp)
    app.register_blueprint(trend_bp)
    app.register_blueprint(realestate_bp)
    
    # Register enhanced strategy blueprint - now the only strategy-related blueprint
    try:
        register_enhanced_strategy(app)
        logger.info("Enhanced Strategy Hub blueprint registered successfully")
    except NameError:
        logger.error("Enhanced Strategy Hub blueprint not registered due to import failure")
        logger.error("This is a critical error as the Enhanced Strategy Hub is now the main strategy interface")
    
    # Register stories blueprint - modular implementation with UUID-based identification
    try:
        register_stories(app)
        logger.info("Stories blueprint registered successfully")
    except NameError:
        logger.warning("Stories blueprint not registered due to import failure")
    
    # Register strategy redirect blueprint - for backward compatibility
    try:
        register_strategy_redirect(app)
        logger.info("Strategy redirect blueprint registered successfully")
    except NameError:
        logger.warning("Strategy redirect blueprint not registered due to import failure")
    
    # Register science-based targets blueprint
    try:
        app.register_blueprint(sbti_bp)
        logger.info("Science-Based Targets blueprint registered successfully")
    except NameError:
        logger.warning("Science-Based Targets blueprint not registered due to import failure")
    
    # Regulatory AI functionality has been consolidated into Data Moat
    # No separate registration is needed
    
    # Register data moat blueprint
    try:
        register_data_moat(app)
        logger.info("Data Moat blueprint registered successfully")
    except NameError:
        logger.warning("Data Moat blueprint not registered due to import failure")
        
    # Register document routes blueprint
    try:
        register_document_routes(app)
        logger.info("Document routes blueprint registered successfully")
    except NameError:
        logger.warning("Document routes blueprint not registered due to import failure")
    
    # Register legacy routes blueprint for backward compatibility
    try:
        from .legacy import legacy_bp, register_blueprint as register_legacy
        register_legacy(app)
        logger.info("Legacy routes blueprint registered successfully")
    except ImportError as e:
        logger.warning(f"Legacy routes blueprint import failed: {str(e)}")
    
    logger.info("All blueprints registered successfully")