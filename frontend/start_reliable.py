#!/usr/bin/env python3
"""
Reliable starter script for Flask frontend
This script ensures clean startup by handling port conflicts
"""
import os
import sys
import signal
import socket
import time
import subprocess
import logging
import psutil

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Get port from environment variable or use 5000 as default
FLASK_PORT = int(os.environ.get('FLASK_PORT', 5000))
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds

def is_port_in_use(port):
    """Check if the port is already in use"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def find_and_terminate_process_by_port(port):
    """Find and terminate any process using the specified port"""
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            # Get connections after we have the process object
            for conn in proc.connections(kind='inet'):
                if conn.laddr.port == port:
                    logger.info(f"Found process using port {port}: PID={proc.pid}, Name={proc.name()}")
                    logger.info(f"Terminating process {proc.pid}")

                    # Try graceful termination first
                    proc.terminate()
                    gone, still_alive = psutil.wait_procs([proc], timeout=3)

                    if still_alive:
                        # Force kill if still alive
                        logger.warning(f"Process {proc.pid} did not terminate gracefully, killing it")
                        proc.kill()

                    return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess, AttributeError):
            # Added AttributeError to handle cases where connections() isn't available
            continue

    return False

def start_flask_app():
    """Start the Flask application with retries"""
    script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "direct_app.py")

    if not os.path.exists(script_path):
        logger.error(f"Flask application script not found at: {script_path}")
        return False

    for attempt in range(MAX_RETRIES):
        if is_port_in_use(FLASK_PORT):
            logger.warning(f"Port {FLASK_PORT} is already in use. Attempting to free it up.")
            if find_and_terminate_process_by_port(FLASK_PORT):
                logger.info(f"Successfully terminated process using port {FLASK_PORT}")
            else:
                logger.warning(f"Could not find process using port {FLASK_PORT}")

            # Wait a moment for the port to be released
            time.sleep(RETRY_DELAY)

            if is_port_in_use(FLASK_PORT) and attempt == MAX_RETRIES - 1:
                logger.error(f"Port {FLASK_PORT} is still in use after {MAX_RETRIES} attempts. Giving up.")
                return False

        logger.info(f"Starting Flask application on port {FLASK_PORT}")
        try:
            # Execute the Flask app as a subprocess
            process = subprocess.Popen([sys.executable, script_path])

            # Wait for the app to start
            for _ in range(10):  # Check for 10 seconds
                time.sleep(1)
                if is_port_in_use(FLASK_PORT):
                    logger.info(f"Flask application is running on port {FLASK_PORT}")
                    return process

            # If we got here, the app didn't start
            logger.error("Flask application failed to start within the expected time")
            process.terminate()
            return False

        except Exception as e:
            logger.error(f"Error starting Flask application: {str(e)}")
            if attempt < MAX_RETRIES - 1:
                logger.info(f"Retrying in {RETRY_DELAY} seconds...")
                time.sleep(RETRY_DELAY)
            else:
                logger.error(f"Failed to start Flask application after {MAX_RETRIES} attempts")
                return False

    return False

if __name__ == "__main__":
    logger.info("Starting reliable Flask starter")

    try:
        # Change to the frontend directory if needed
        if not os.path.exists("direct_app.py"):
            os.chdir("frontend")

        # Start the Flask application
        flask_process = start_flask_app()

        if flask_process:
            # Keep the script running
            logger.info("Flask application started successfully. Press Ctrl+C to stop.")
            try:
                flask_process.wait()
            except KeyboardInterrupt:
                logger.info("Stopping Flask application...")
                flask_process.terminate()
        else:
            logger.error("Failed to start Flask application")
            sys.exit(1)

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        sys.exit(1)