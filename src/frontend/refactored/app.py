"""
Main application module for the SustainaTrend™ Intelligence Platform.
"""
import os
import sys
import logging
import traceback
from logging.handlers import RotatingFileHandler
from flask import Flask, jsonify, render_template, redirect, url_for, request
from dotenv import load_dotenv
from datetime import datetime
from waitress import serve
from flask_session import Session
from src.frontend.refactored.services.mongodb_service import MongoDBService
from src.frontend.refactored.routes import main, analytics, vc_lens, realestate, strategy, monetization

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, project_root)

# Load environment variables
load_dotenv()

# Configure logging
def setup_logging():
    """Configure logging for the application."""
    log_dir = os.path.join(project_root, 'logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    log_file = os.path.join(log_dir, 'app.log')
    
    # Create a formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create a file handler with rotation
    file_handler = RotatingFileHandler(
        log_file, maxBytes=10*1024*1024, backupCount=5
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)
    
    # Create a console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)
    
    # Configure the root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Remove any existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Add the handlers
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    # Log application startup
    logging.info("SustainaTrend™ application starting up")

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__,
                template_folder=os.path.join(os.path.dirname(__file__), 'templates'),
                static_folder=os.path.join(os.path.dirname(__file__), 'static'))
    
    # Configure logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # Configure app
    app.config.update(
        SECRET_KEY=os.getenv('SECRET_KEY', 'your-secret-key-here'),
        SESSION_TYPE='filesystem',
        MONGODB_URI=os.getenv('MONGODB_URI'),
        ADMIN_KEY=os.getenv('ADMIN_KEY', 'dev-admin-key'),
        VERSION='1.0.0',
        DEBUG=os.getenv('FLASK_ENV') == 'development',
        HOST=os.getenv('HOST', '127.0.0.1'),
        PORT=int(os.getenv('PORT', 5000)),
        MAX_CONTENT_LENGTH=16 * 1024 * 1024  # 16MB max file size
    )
    
    # Initialize extensions
    Session(app)
    
    # Initialize MongoDB service
    try:
        mongodb = MongoDBService()
        app.mongodb = mongodb
        logger.info("MongoDB service initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize MongoDB service: {str(e)}")
        logger.error(traceback.format_exc())
        app.mongodb = None
    
    # Register blueprints
    app.register_blueprint(main.main_bp)
    app.register_blueprint(analytics.analytics_bp)
    app.register_blueprint(vc_lens.vc_lens_bp)
    app.register_blueprint(realestate.realestate_bp)
    app.register_blueprint(strategy.strategy_bp)
    app.register_blueprint(monetization.monetization_bp)
    
    # Request logging middleware
    @app.before_request
    def log_request_info():
        logger.info(f"Request: {request.method} {request.url}")
        if request.is_json:
            logger.info(f"JSON data: {request.get_json()}")
    
    # Response logging middleware
    @app.after_request
    def log_response_info(response):
        logger.info(f"Response: {response.status}")
        return response
    
    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        logger.warning(f"404 error: {request.url}")
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"500 error: {str(error)}")
        logger.error(traceback.format_exc())
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(403)
    def forbidden_error(error):
        logger.warning(f"403 error: {request.url}")
        return render_template('errors/404.html'), 403  # Reuse 404 template for security
    
    @app.errorhandler(400)
    def bad_request_error(error):
        logger.warning(f"400 error: {request.url}")
        return render_template('errors/500.html'), 400  # Reuse 500 template for client errors
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        mongodb_status = 'healthy' if app.mongodb and app.mongodb.is_connected() else 'unhealthy'
        return jsonify({
            'status': 'healthy',
            'mongodb_status': mongodb_status,
            'timestamp': datetime.now().isoformat(),
            'version': app.config['VERSION'],
            'environment': 'development' if app.config['DEBUG'] else 'production'
        })
    
    # Root route - redirect to dashboard
    @app.route('/')
    def index():
        return redirect(url_for('main.dashboard'))
    
    return app

def run_app():
    """Run the application using the appropriate server."""
    setup_logging()
    app = create_app()
    host = app.config['HOST']
    port = app.config['PORT']
    debug = app.config['DEBUG']
    
    logging.info(f"Starting server on {host}:{port} (debug={debug})")
    
    if debug:
        # Use Flask's development server in debug mode
        app.run(host=host, port=port, debug=True)
    else:
        # Use Waitress for production
        serve(app, host=host, port=port)

if __name__ == '__main__':
    run_app() 