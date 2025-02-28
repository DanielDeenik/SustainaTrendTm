#!/usr/bin/env python3
"""
Reliable starter script for Flask frontend
This script ensures clean startup by handling port conflicts
"""
import os
import sys
import signal
import logging
from port_manager import PortManager

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Get port from environment variable or use 5000 as default
FLASK_PORT = int(os.environ.get('FLASK_PORT', 5000))

def signal_handler(sig, frame):
    """Handle termination signals"""
    logger.info("Received termination signal, shutting down...")
    sys.exit(0)

def main():
    """Main function to start the Flask application reliably"""
    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    logger.info("Starting reliable Flask starter")

    try:
        # Change to the frontend directory if needed
        if not os.path.exists("direct_app.py"):
            current_dir = os.getcwd()
            if os.path.basename(current_dir) != "frontend" and os.path.isdir("frontend"):
                os.chdir("frontend")
                logger.info("Changed working directory to frontend")

        # Get the Flask application path
        script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "direct_app.py")
        if not os.path.exists(script_path):
            script_path = "direct_app.py"  # Try relative path
            if not os.path.exists(script_path):
                logger.error("Flask application script not found")
                return 1

        # Create and use the port manager to run our Flask app
        port_manager = PortManager(port=FLASK_PORT, max_retries=5, timeout=15)

        # First ensure the port is free
        if not port_manager.free_port():
            logger.error(f"Failed to free port {FLASK_PORT} after multiple attempts")
            return 1

        # Run the Flask application
        logger.info(f"Starting Flask application on port {FLASK_PORT}")
        flask_process = port_manager.run_flask_app(script_path)

        if flask_process:
            # App started successfully
            logger.info("Flask application started successfully. Press Ctrl+C to stop.")
            try:
                # Keep the script running until the process exits or is interrupted
                return_code = flask_process.wait()
                logger.info(f"Flask application exited with code {return_code}")
                return return_code
            except KeyboardInterrupt:
                logger.info("Stopping Flask application...")
                port_manager.stop_app()
        else:
            logger.error("Failed to start Flask application")
            return 1

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())