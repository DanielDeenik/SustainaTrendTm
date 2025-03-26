"""
Start script for Replit environment to ensure proper binding 
for the Sustainability Intelligence Platform.

This script ensures the Flask application correctly binds to the 
host and port expected by Replit's proxying system.
"""

import os
import sys
import logging
from app import create_app

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("logs/replit_startup.log")
    ]
)

logger = logging.getLogger("replit_startup")

def main():
    """Main entry point function optimized for Replit"""
    # Create log directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)
    
    logger.info("Starting SustainaTrend Intelligence Platform for Replit")
    logger.info(f"Current working directory: {os.getcwd()}")
    
    # Set Replit-specific environment variables 
    # to ensure proper connectivity
    os.environ['REPLIT_ENVIRONMENT'] = 'true'
    
    # For Replit, we need to ensure we're binding to the correct port
    # Replit expects us to use port 3000, 5000, 8080, or env PORT variable
    port = int(os.environ.get('PORT', 5000))
    host = '0.0.0.0'  # Always bind to all interfaces in Replit
    os.environ['HOST'] = host
    os.environ['PORT'] = str(port)
    
    logger.info(f"Replit config: Setting up server at {host}:{port}")
    
    # Create Flask application
    app = create_app()
    
    # Use the configured host and port
    debug = os.environ.get('FLASK_ENV', 'development') == 'development'
    
    # Log the registered routes and server configuration
    logger.info(f"Registered routes: {len(list(app.url_map.iter_rules()))}")
    logger.info(f"Starting Flask server on {host}:{port} with debug={debug}")
    
    # Run the application with the specified host and port
    # This will make the app accessible to Replit's proxying system
    app.run(host=host, port=port, debug=debug)

if __name__ == '__main__':
    main()