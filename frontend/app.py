#!/usr/bin/env python3
"""
Bridge file to run the enhanced direct_app.py code
while maintaining compatibility with Replit configuration
"""
import logging
import os
import sys
import traceback

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info("Starting bridge to Sustainability Intelligence Dashboard")
logger.info(f"Current working directory: {os.getcwd()}")
logger.info(f"Python executable: {sys.executable}")
logger.info(f"Python path: {sys.path}")

# Check if direct_app.py exists
direct_app_path = os.path.join(os.getcwd(), "direct_app.py")
if os.path.exists(direct_app_path):
    logger.info(f"direct_app.py found at {direct_app_path}")
else:
    logger.error(f"direct_app.py not found at {direct_app_path}")
    # List directory contents to debug
    logger.info(f"Directory contents: {os.listdir(os.getcwd())}")

# Import the app and all functionality from direct_app.py
try:
    # This will import all the routes and functionality we've enhanced
    from direct_app import app, logger
    
    # Import and register unified routes
    try:
        from unified_routes import register_unified_routes
        register_unified_routes(app)
        logger.info("Unified routes registered successfully")
    except ImportError as e:
        logger.warning(f"Unified routes could not be registered: {e}")

    # Log all registered routes for debugging
    routes = [str(rule) for rule in app.url_map.iter_rules()]
    logger.info(f"Successfully imported enhanced application from direct_app.py")
    logger.info(f"Registered routes: {routes}")

    if __name__ == "__main__":
        # Use port 5000 to match Replit's expected configuration
        port = 5000
        logger.info(f"Starting Flask server on port {port}")

        # Start Flask server - use host 0.0.0.0 to make it accessible from outside the container
        app.run(host="0.0.0.0", port=port, debug=True)
except Exception as e:
    logger.error(f"Error importing or running enhanced application: {str(e)}")
    logger.error(traceback.format_exc())

    # Fall back to original implementation if there's an issue with direct_app.py
    # This preserves the original functionality in case of problems
    from flask import Flask, render_template, jsonify, request
    import requests
    from flask_caching import Cache
    from datetime import datetime, timedelta
    import json

    logger.warning("Falling back to basic implementation due to error")

    # Initialize Flask
    app = Flask(__name__)

    # Setup Simple Cache
    cache = Cache(app, config={
        'CACHE_TYPE': 'SimpleCache'
    })

    # Add basic routes with debug info
    @app.route('/')
    def home():
        """Home page"""
        logger.info(f"Home route called (fallback mode)")
        return render_template("index.html")

    @app.route('/search')
    def search():
        """Search route (fallback)"""
        logger.info(f"Search route called (fallback mode)")
        query = request.args.get('query', '')
        return render_template("search.html", query=query, model="rag", results=[])

    @app.route('/trend-analysis')
    def trend_analysis():
        """Trend analysis route (fallback)"""
        logger.info(f"Trend analysis route called (fallback mode)")
        return render_template("trend_analysis.html", trends=[], trend_chart_data=[], category="all", sort="virality")

    @app.route('/debug')
    def debug_route():
        """Debug route to check registered routes"""
        logger.info(f"Debug route called (fallback mode)")
        routes = [str(rule) for rule in app.url_map.iter_rules()]
        python_info = {
            "sys.path": sys.path,
            "current_dir": os.getcwd(),
            "dir_contents": os.listdir(os.getcwd()),
            "error": str(e),
            "traceback": traceback.format_exc()
        }
        return jsonify({"routes": routes, "python_info": python_info})

    if __name__ == "__main__":
        # ALWAYS serve the app on port 5000
        logger.info("Starting fallback Flask server on port 5000")
        routes = [str(rule) for rule in app.url_map.iter_rules()]
        logger.info(f"Registered routes (fallback): {routes}")
        app.run(host="0.0.0.0", port=5000, debug=True)