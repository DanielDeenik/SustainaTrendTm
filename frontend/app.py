"""
SustainaTrend Intelligence Platform - Application Factory

This file serves as the main entry point for the Flask application with a clean,
modular blueprint-based architecture.
"""
import logging
logger = logging.getLogger(__name__)

import os
import logging
from flask import Flask, request, g
from logging.config import dictConfig

# Configure logging
def configure_logging():
    """Configure logging for the application"""
    dictConfig({
        'version': 1,
        'formatters': {
            'default': {
                'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'level': 'INFO',
                'formatter': 'default',
                'stream': 'ext://sys.stdout',
            },
            'file': {
                'class': 'logging.FileHandler',
                'level': 'INFO',
                'formatter': 'default',
                'filename': 'app.log',
            }
        },
        'root': {
            'level': 'INFO',
            'handlers': ['console', 'file']
        }
    })

def create_app(test_config=None):
    """
    Create and configure the Flask application
    
    Args:
        test_config: Configuration dictionary for testing (optional)
        
    Returns:
        Flask application instance
    """
    # Configure logging
    configure_logging()
    
    # Create Flask application
    app = Flask(__name__)
    
    # Configure the application
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev'),
        DEBUG=os.environ.get('FLASK_ENV', 'development') == 'development',
    )
    
    if test_config:
        app.config.update(test_config)
    
    # Initialize the application
    @app.before_request
    def before_request():
        """Execute before each request"""
        g.theme = request.cookies.get('theme', 'dark')
    
    # Register template context processors
    @app.context_processor
    def inject_api_status():
        """Inject API status into all templates"""
        from direct_app import get_api_status
        return {"api_status": get_api_status()}
    
    @app.context_processor
    def inject_theme_preference():
        """Inject theme preference into all templates"""
        return {"theme": g.get('theme', 'dark')}
    
    # Register blueprints
    from routes import register_blueprints
    register_blueprints(app)
    
    # Register API blueprint routes separately
    from routes.api import api_bp
    app.register_blueprint(api_bp)
    
    # Register the API views blueprint
    from routes.api import api_views_bp
    try:
        app.register_blueprint(api_views_bp)
        app.logger.info("API views blueprint registered successfully")
    except Exception as e:
        app.logger.error(f"Error registering API views blueprint: {e}")
    
    # Directly register the Regulatory AI blueprint to ensure it's available
    try:
        # Import the blueprint directly from the module
        import frontend.regulatory_ai_agent as reg_module
        app.register_blueprint(reg_module.regulatory_ai_bp)
        app.logger.info("Regulatory AI blueprint registered directly in app.py")
    except Exception as e:
        app.logger.error(f"Error directly registering Regulatory AI blueprint: {e}")
        try:
            # Alternative import path
            import regulatory_ai_agent as reg_module
            app.register_blueprint(reg_module.regulatory_ai_bp)
            app.logger.info("Regulatory AI blueprint registered directly in app.py (alternative path)")
        except Exception as e2:
            app.logger.error(f"Error with alternative Regulatory AI blueprint registration: {e2}")
    
    # Log the registered routes
    app.logger.info(f"Registered routes: {len(list(app.url_map.iter_rules()))}")
    
    return app
    
# If this file is run directly, start the application
if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)