"""
Run script for SustainaTrend Intelligence Platform - Clean App Factory

This script serves as the entry point for starting the Flask application
using the app factory pattern.
"""

import os
import sys
import logging
from app import create_app

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)

def main():
    """Main entry point function"""
    logger.info("Starting SustainaTrend Intelligence Platform")
    
    # Log useful debugging information
    logger.info(f"Current working directory: {os.getcwd()}")
    logger.info(f"Python executable: {sys.executable}")
    logger.info(f"Python path: {sys.path}")
    
    # Create Flask application
    app = create_app()
    
    # Log the registered routes
    logger.info(f"Registered routes: {len(list(app.url_map.iter_rules()))}")
    
    # Run the application
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV', 'development') == 'development'
    
    logger.info(f"Starting Flask server on {host}:{port}")
    app.run(host=host, port=port, debug=debug)

if __name__ == '__main__':
    main()