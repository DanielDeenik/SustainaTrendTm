"""
Main application module for the SustainaTrend™ Intelligence Platform.
"""
import os
import sys
import logging
import traceback
import atexit
from logging.handlers import RotatingFileHandler
from flask import Flask, jsonify, render_template, redirect, url_for, request
from datetime import datetime
from waitress import serve
from flask_session import Session
from src.frontend.refactored.services.mongodb_service import mongodb_service
from src.frontend.refactored.services.config_service import config_service
from src.frontend.refactored.routes import main, analytics, vc_lens, realestate, strategy, monetization
from src.frontend.refactored.services.monitoring_service import monitoring_service
from src.frontend.refactored.routes.analytics import analytics_bp
from src.frontend.refactored.routes.vc_lens import vc_lens_bp
from src.frontend.refactored.routes.monitoring import monitoring_bp

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, project_root)

# Configure module-level logger
logger = logging.getLogger(__name__)

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
    logger.info("SustainaTrend™ application starting up")

def create_app(config=None):
    """Create and configure the Flask application."""
    app = Flask(__name__,
                template_folder=os.path.join(os.path.dirname(__file__), 'templates'),
                static_folder=os.path.join(os.path.dirname(__file__), 'static'))
    
    # Configure logging
    setup_logging()
    
    # Load configuration
    if config is None:
        config = os.getenv('FLASK_CONFIG', 'development')
    app.config.from_object(f'config.{config.capitalize()}Config')
    
    # Ensure upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Initialize extensions
    Session(app)
    
    # Add template filters
    @app.template_filter('format_number')
    def format_number(value):
        """Format a number with commas and optional decimal places."""
        try:
            if isinstance(value, (int, float)):
                return f"{value:,.2f}".rstrip('0').rstrip('.')
            return value
        except:
            return value
    
    # Initialize MongoDB service
    try:
        # Use the singleton instance from the mongodb_service module
        app.mongodb = mongodb_service
        
        # Register shutdown hook to close MongoDB connection
        atexit.register(mongodb_service.close)
        
        if not mongodb_service.is_connected():
            logger.warning("MongoDB service not connected. Check configuration.")
        else:
            logger.info("MongoDB service initialized and connected successfully")
    except Exception as e:
        logger.error(f"Failed to initialize MongoDB service: {str(e)}")
        logger.error(traceback.format_exc())
        app.mongodb = None
    
    # Register blueprints
    app.register_blueprint(main.main_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(vc_lens_bp)
    app.register_blueprint(realestate.realestate_bp)
    app.register_blueprint(strategy.strategy_bp)
    app.register_blueprint(monetization.monetization_bp)
    app.register_blueprint(monitoring_bp)
    
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
    host = config_service.get_host()
    port = config_service.get_port()
    debug = config_service.is_debug()
    
    logger.info(f"Starting server on {host}:{port} (debug={debug})")
    
    if debug:
        # Development server
        app.run(host=host, port=port, debug=True)
    else:
        # Production server (Waitress)
        logger.info("Starting production server (Waitress)")
        serve(app, host=host, port=port, threads=4)

if __name__ == '__main__':
    run_app() 