"""
SustainaTrend Intelligence Platform - Frontend Entry Point (Transitional)

This file is being maintained for backward compatibility and redirects
to the consolidated_app.py implementation.
"""
import os
import sys
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add parent directory to path so we can import consolidated_app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    # Import the functions from consolidated_app
    from consolidated_app import create_app as consolidated_create_app
    logger.info("Successfully imported consolidated_app")
except ImportError as e:
    logger.error(f"Failed to import consolidated_app: {e}")
    raise

# Import Flask for typing information
import flask
from flask import Flask

def create_app(test_config=None):
    """
    Simply passes through to consolidated_app.create_app
    
    Args:
        test_config: Configuration dictionary for testing (optional)
        
    Returns:
        Flask application instance from consolidated_app
    """
    logger.info("Redirecting to consolidated_app.create_app")
    return consolidated_create_app(test_config)
    
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