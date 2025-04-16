"""
Main entry point for the frontend application.

This module initializes the Flask application and registers all blueprints.
"""

import os
import logging
from datetime import datetime
from flask import Flask, render_template, jsonify
from dotenv import load_dotenv
from flask_session import Session
from datetime import timedelta

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def create_app():
    """Create and configure the Flask application."""
    try:
        app = Flask(__name__)
        
        # Configure app
        app.config.update(
            SECRET_KEY=os.getenv('SECRET_KEY', 'dev'),
            SESSION_TYPE='filesystem',
            PERMANENT_SESSION_LIFETIME=timedelta(days=1),
            SESSION_FILE_DIR='flask_session',
            SESSION_FILE_THRESHOLD=500
        )
        
        # Initialize session
        Session(app)
        
        # Register error handlers
        @app.errorhandler(404)
        def not_found_error(error):
            logger.error(f"Page not found: {error}")
            return render_template('errors/404.html'), 404
            
        @app.errorhandler(500)
        def internal_error(error):
            logger.error(f"Internal server error: {error}")
            return render_template('errors/500.html'), 500
            
        # Register blueprints
        try:
            from routes.main import main_bp
            from routes.auth import auth_bp
            from routes.analytics import analytics_bp
            from routes.api import api_bp
            from routes.vc_lens import vc_lens_bp
            from routes.strategy import strategy_bp
            from routes.dashboard import dashboard_bp
            from routes.trend import trend_bp
            from routes.realestate import realestate_bp
            from routes.storytelling import storytelling_bp
            
            app.register_blueprint(main_bp)
            app.register_blueprint(auth_bp, url_prefix='/auth')
            app.register_blueprint(analytics_bp, url_prefix='/analytics')
            app.register_blueprint(api_bp, url_prefix='/api')
            app.register_blueprint(vc_lens_bp, url_prefix='/vc-lens')
            app.register_blueprint(strategy_bp, url_prefix='/strategy')
            app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
            app.register_blueprint(trend_bp, url_prefix='/trend')
            app.register_blueprint(realestate_bp, url_prefix='/realestate')
            app.register_blueprint(storytelling_bp, url_prefix='/storytelling')
            
            logger.info("All blueprints registered successfully")
        except Exception as e:
            logger.error(f"Error registering blueprints: {str(e)}")
            raise
            
        # Health check endpoint
        @app.route('/health')
        def health_check():
            return jsonify({
                'status': 'healthy',
                'timestamp': datetime.now().isoformat()
            })
            
        return app
        
    except Exception as e:
        logger.error(f"Error creating Flask application: {str(e)}")
        raise

def main():
    """Main entry point for the application."""
    try:
        app = create_app()
        
        # Get port from environment or use default
        port = int(os.getenv('PORT', 5000))
        host = os.getenv('HOST', '0.0.0.0')
        
        # Run the application
        app.run(host=host, port=port, debug=os.getenv('DEBUG', 'False').lower() == 'true')
        
    except Exception as e:
        logger.error(f"Application failed to start: {str(e)}")
        raise

if __name__ == '__main__':
    main()