#!/usr/bin/env python3
"""
Entry point for SustainaTrend Intelligence Platform

This file serves as the main entry point for the Flask application and
maintains compatibility with Replit configuration. The application uses
clean_app.py with consolidated routes in updated_routes.py.
"""
import logging
import os
import sys
import traceback
import argparse

# Parse command line arguments
parser = argparse.ArgumentParser(description='Start the SustainaTrend Intelligence Platform')
parser.add_argument('--port', type=int, default=int(os.environ.get('PORT', 5000)), help='Port to run the server on')
parser.add_argument('--debug', action='store_true', default=True, help='Run in debug mode')
args = parser.parse_args()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info("Starting SustainaTrend Intelligence Platform")
logger.info(f"Current working directory: {os.getcwd()}")
logger.info(f"Python executable: {sys.executable}")
logger.info(f"Python path: {sys.path}")

# Import the application from clean_app.py
try:
    logger.info("Loading application from clean_app.py")
    from clean_app import app, create_app
    
    # Log all registered routes for debugging
    routes = [str(rule) for rule in app.url_map.iter_rules()]
    logger.info(f"Successfully imported application from clean_app.py")
    logger.info(f"Registered routes: {len(routes)}")
    
except Exception as e:
    logger.error(f"Error importing application: {str(e)}")
    logger.error(traceback.format_exc())
    
    # Fall back to minimal implementation if all else fails
    from flask import Flask, render_template, jsonify, request
    from flask_caching import Cache

    logger.warning("Falling back to minimal implementation due to errors")

    # Initialize Flask
    app = Flask(__name__)

    # Setup Simple Cache
    cache = Cache(app, config={
        'CACHE_TYPE': 'SimpleCache'
    })

    # Add basic emergency routes with debug info
    @app.route('/')
    def home():
        """Home page"""
        logger.info(f"Home route called (emergency fallback mode)")
        return render_template("index.html")

    @app.route('/debug')
    def debug_route():
        """Debug route to check registered routes"""
        logger.info(f"Debug route called (emergency fallback mode)")
        routes = [str(rule) for rule in app.url_map.iter_rules()]
        python_info = {
            "sys.path": sys.path,
            "current_dir": os.getcwd(),
            "dir_contents": os.listdir(os.getcwd()),
            "error": str(e),
            "traceback": traceback.format_exc()
        }
        return jsonify({"routes": routes, "python_info": python_info})

# Start the application when run directly
if __name__ == "__main__":
    # Use port 5000 to match Replit's expected configuration
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"Starting Flask server on port {port}")
    app.run(host="0.0.0.0", port=port, debug=True)