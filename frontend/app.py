#!/usr/bin/env python3
"""
Entry point for SustainaTrend Intelligence Platform

This file serves as the main entry point for the Flask application and
maintains compatibility with Replit configuration.
"""
import logging
import os
import sys
import traceback

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info("Starting SustainaTrend Intelligence Platform")
logger.info(f"Current working directory: {os.getcwd()}")
logger.info(f"Python executable: {sys.executable}")
logger.info(f"Python path: {sys.path}")

# Try to import from clean_app.py first
try:
    logger.info("Loading application from clean_app.py")
    from clean_app import app
    
    # Log all registered routes for debugging
    routes = [str(rule) for rule in app.url_map.iter_rules()]
    logger.info(f"Successfully imported application from clean_app.py")
    logger.info(f"Registered routes: {len(routes)}")
    
    # Start the application when run directly
    if __name__ == "__main__":
        # Use port 5000 to match Replit's expected configuration
        port = int(os.environ.get('PORT', 5000))
        logger.info(f"Starting Flask server on port {port}")
        app.run(host="0.0.0.0", port=port, debug=True)
        
except ImportError:
    logger.warning("Could not import from clean_app.py, trying direct_app.py")
    
    # Fall back to direct_app.py if clean_app.py is not available
    try:
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
        logger.info(f"Registered routes: {len(routes)}")
    
        if __name__ == "__main__":
            # Use port 5000 to match Replit's expected configuration
            port = int(os.environ.get('PORT', 5000))
            logger.info(f"Starting Flask server on port {port}")
            app.run(host="0.0.0.0", port=port, debug=True)
            
    except Exception as e:
        logger.error(f"Error importing or running enhanced application: {str(e)}")
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
            return render_template("trend_analysis.html", category="all", sort="virality")
    
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
            port = int(os.environ.get('PORT', 5000))
            logger.info(f"Starting fallback Flask server on port {port}")
            routes = [str(rule) for rule in app.url_map.iter_rules()]
            logger.info(f"Registered routes (fallback): {len(routes)}")
            app.run(host="0.0.0.0", port=port, debug=True)