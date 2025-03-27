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
        # Replit specific configurations
        SERVER_NAME=None,  # Set to None to handle Replit's proxy
        PREFERRED_URL_SCHEME='https',
        APPLICATION_ROOT='/',
    )
    
    # Replit-specific configuration for proxy
    if os.environ.get('REPLIT_ENVIRONMENT') == 'true':
        from werkzeug.middleware.proxy_fix import ProxyFix
        app.wsgi_app = ProxyFix(
            app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
        )
        app.logger.info("Configured ProxyFix middleware for Replit environment")
    
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
    
    # The Strategy Hub blueprint is now registered via routes/__init__.py
    # Removed direct registration to avoid duplicate registration
    app.logger.info("Strategy Hub blueprint is registered through routes/__init__.py")
    
    # Note: Regulatory AI blueprints are also registered exclusively through routes/__init__.py
    app.logger.info("Regulatory AI blueprints are registered through routes/__init__.py")
    
    # Add home route that redirects to dashboard (2025 refresh)
    @app.route('/')
    def home():
        """Redirect to dashboard as the primary landing page for 2025 refresh"""
        from flask import redirect
        app.logger.info("Home route redirecting to dashboard")
        return redirect('/dashboard/')
    
    # Register direct document upload shortcut
    @app.route('/document-upload-standalone')
    def document_upload_standalone():
        """Redirect to standalone document upload on port 7000"""
        from flask import redirect
        host = request.host.split(':')[0]  # Get hostname without port
        return redirect(f'http://{host}:7000')
    
    # Log the registered routes
    app.logger.info(f"Registered routes: {len(list(app.url_map.iter_rules()))}")
    
    return app
    
# If this file is run directly, start the application
if __name__ == "__main__":
    app = create_app()
    
    # Get host and port from environment variables with defaults
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV', 'development') == 'development'
    
    # Log the server startup information
    print(f"Starting Flask server on {host}:{port} with debug={debug}")
    app.logger.info(f"Starting Flask server on {host}:{port} with debug={debug}")
    
    # Run the application with the specified host and port
    app.run(host=host, port=port, debug=debug)