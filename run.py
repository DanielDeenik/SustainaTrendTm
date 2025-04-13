#!/usr/bin/env python
"""
SustainaTrend™ Intelligence Platform - Application Launcher
This script launches the SustainaTrend application using either Flask's development server
or Waitress for production deployment.
"""

import os
import sys
import logging
from dotenv import load_dotenv
from waitress import serve

# Add src directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=os.getenv('LOG_LEVEL', 'INFO'),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.getenv('LOG_FILE', 'logs/app.log')),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def main():
    """Launch the application based on environment configuration."""
    try:
        from frontend.app import create_app
        
        # Create Flask application
        app = create_app()
        
        # Get configuration from environment
        host = os.getenv('HOST', '127.0.0.1')
        port = int(os.getenv('PORT', 5000))
        debug = os.getenv('DEBUG', 'False').lower() == 'true'
        
        if debug:
            logger.info(f"Starting development server on {host}:{port}")
            app.run(host=host, port=port, debug=True)
        else:
            logger.info(f"Starting production server on {host}:{port}")
            serve(app, host=host, port=port)
            
    except Exception as e:
        logger.error(f"Failed to start application: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main() 