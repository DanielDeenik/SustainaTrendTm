#!/usr/bin/env python3
"""
SustainaTrend Intelligence Platform - Clean Application Entry Point

This file serves as the entry point for the Flask application with a cleaner,
more organized structure using modular routing.
"""
import logging
import os
import sys
try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = lambda: None
    print("Warning: python-dotenv not installed, environment variables may not be properly loaded")

try:
    from flask import Flask, request, render_template
    from flask_caching import Cache
except ImportError:
    print("Error: Flask or Flask-Caching not installed")
    sys.exit(1)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info("Starting SustainaTrend Intelligence Platform")

# Load environment variables
load_dotenv()

def create_app():
    """
    Create and configure the Flask application
    
    Returns:
        Flask application instance
    """
    # Initialize Flask
    app = Flask(__name__)
    
    # Configure app
    app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', 'sustainatrend-platform-secret-key-2025')
    
    # Setup cache
    cache = Cache(app, config={
        'CACHE_TYPE': 'SimpleCache'
    })
    
    # Register API status context processor
    @app.context_processor
    def inject_api_status():
        """Inject API status into all templates"""
        from direct_app import get_api_status
        return {
            "api_status": get_api_status()
        }
    
    # Register theme preference context processor
    @app.context_processor
    def inject_theme_preference():
        """Inject theme preference into all templates"""
        theme = request.args.get('theme', '')
        
        # Convert to template class name
        current_theme = 'dark-mode'  # Default
        if theme == 'light':
            current_theme = 'light-mode'
        elif theme == 'dark':
            current_theme = 'dark-mode'
        
        return {
            "current_theme": current_theme
        }
    
    # Import and register routes
    try:
        # Try to use the updated consolidated routes first
        from updated_routes import register_routes
        register_routes(app)
        logger.info("Consolidated routes registered successfully")
    except ImportError as e:
        logger.warning(f"Failed to register consolidated routes: {e}")
        # Try to use the cleaned, streamlined routes next
        try:
            from cleaned_routes import register_routes
            register_routes(app)
            logger.info("Streamlined routes registered successfully")
        except ImportError as e:
            logger.warning(f"Failed to register streamlined routes: {e}")
            # Fall back to original routes if needed
            try:
                from routes import register_routes
                register_routes(app)
                logger.info("Original routes registered successfully")
            except ImportError as e:
                logger.error(f"Failed to register original routes: {e}")
                # In case of import error, use fallback
                logger.warning("Using direct_app.py as fallback")
                try:
                    from direct_app import app as direct_app
                    app = direct_app
                except ImportError:
                    logger.error("Failed to import direct_app.py as fallback")
    
    # Document query API routes are now handled in updated_routes.py
    logger.info("Document query API routes are now registered via updated_routes.py")
    
    # Monetization strategies routes are now handled in updated_routes.py
    logger.info("Monetization strategies routes are now registered via updated_routes.py")
    
    # Debug route is now in updated_routes.py
    
    return app

# Create the application
app = create_app()

if __name__ == "__main__":
    # Parse command line arguments
    import argparse
    
    parser = argparse.ArgumentParser(description='Run the SustainaTrend Intelligence Platform')
    parser.add_argument('--host', default='0.0.0.0', help='Host to run the server on')
    parser.add_argument('--port', type=int, default=int(os.environ.get('PORT', 5000)), help='Port to run the server on')
    parser.add_argument('--debug', action='store_true', default=True, help='Run in debug mode')
    
    args = parser.parse_args()
    
    # Start Flask server
    logger.info(f"Starting Flask server on {args.host}:{args.port}")
    app.run(host=args.host, port=args.port, debug=args.debug)