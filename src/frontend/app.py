"""
SustainaTrend™ Intelligence Platform - Frontend Application

This module serves as the main entry point for the frontend application,
providing a web interface for the SustainaTrend™ Intelligence Platform.
"""

import os
import sys
import logging
from flask import Flask, render_template, jsonify, request, send_from_directory
from werkzeug.utils import secure_filename
from datetime import datetime
from flask_session import Session
from dotenv import load_dotenv
from logging.handlers import RotatingFileHandler

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=os.getenv('LOG_LEVEL', 'INFO'),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        RotatingFileHandler('logs/app.log', maxBytes=10485760, backupCount=10),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__, 
                static_folder='static',
                template_folder='templates')
    
    # Configure app
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key-change-in-production')
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SESSION_PERMANENT'] = False
    app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hour
    
    # Initialize extensions
    Session(app)
    
    # Register blueprints
    from frontend.routes.main import main_bp
    from frontend.routes.auth import auth_bp
    from frontend.routes.vc_dashboard import vc_dashboard_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(vc_dashboard_bp, url_prefix='/vc')
    
    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('error.html', message="Page not found"), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Server error: {error}")
        return render_template('error.html', message="An internal server error occurred"), 500
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        return jsonify({"status": "healthy"}), 200
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)), debug=os.getenv('FLASK_ENV') == 'development')