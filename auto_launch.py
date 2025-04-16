#!/usr/bin/env python
"""
Auto-Launch Script for SustainaTrend™

This script automatically launches the SustainaTrend™ application,
monitors for errors, and provides options for conditional shutdown.
"""

import os
import sys
import time
import signal
import subprocess
import requests
import logging
from datetime import datetime
from pathlib import Path

# Configure logging
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)
log_file = log_dir / f"auto_launch_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("auto_launch")

# Configuration
APP_ENTRY_POINT = "run.py"
APP_HOST = "127.0.0.1"
APP_PORT = 5000
STARTUP_WAIT_TIME = 5  # seconds
ROUTES_TO_TEST = [
    "/",
    "/dashboard",
    "/vc-lens",
    "/analytics",
    "/strategy",
    "/realestate",
    "/monetization"
]

def start_application():
    """Start the Flask application as a subprocess."""
    logger.info(f"Starting application from {APP_ENTRY_POINT}")
    try:
        # Start the application in a subprocess
        process = subprocess.Popen(
            [sys.executable, APP_ENTRY_POINT],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        return process
    except Exception as e:
        logger.error(f"Failed to start application: {str(e)}")
        return None

def test_routes():
    """Test application routes for errors."""
    errors_detected = False
    base_url = f"http://{APP_HOST}:{APP_PORT}"
    
    for route in ROUTES_TO_TEST:
        url = f"{base_url}{route}"
        logger.info(f"Testing route: {url}")
        
        try:
            response = requests.get(url, timeout=5)
            if response.status_code != 200:
                logger.error(f"Route {route} returned status code {response.status_code}")
                errors_detected = True
            else:
                logger.info(f"Route {route} is working correctly")
        except requests.exceptions.ConnectionError:
            logger.error(f"Could not connect to {url}")
            errors_detected = True
        except requests.exceptions.Timeout:
            logger.error(f"Request to {url} timed out")
            errors_detected = True
        except Exception as e:
            logger.error(f"Error testing route {route}: {str(e)}")
            errors_detected = True
    
    return errors_detected

def monitor_application(process):
    """Monitor the application process and log output."""
    while True:
        # Check if process is still running
        if process.poll() is not None:
            logger.error("Application process has terminated unexpectedly")
            return False
        
        # Read output from the process
        output = process.stdout.readline()
        if output:
            logger.info(f"App output: {output.strip()}")
        
        # Check for errors in stderr
        error = process.stderr.readline()
        if error:
            logger.error(f"App error: {error.strip()}")
        
        time.sleep(0.1)

def shutdown_application(process):
    """Gracefully shut down the application."""
    logger.info("Shutting down application")
    try:
        # Send SIGTERM signal to the process
        process.terminate()
        
        # Wait for the process to terminate
        process.wait(timeout=5)
        logger.info("Application shut down successfully")
    except subprocess.TimeoutExpired:
        # Force kill if it doesn't terminate gracefully
        logger.warning("Application did not terminate gracefully, forcing shutdown")
        process.kill()
    except Exception as e:
        logger.error(f"Error during shutdown: {str(e)}")

def main():
    """Main function to run the auto-launch script."""
    logger.info("Starting SustainaTrend™ Auto-Launch")
    
    # Start the application
    process = start_application()
    if not process:
        logger.error("Failed to start application, exiting")
        return
    
    # Wait for the application to start
    logger.info(f"Waiting {STARTUP_WAIT_TIME} seconds for application to start")
    time.sleep(STARTUP_WAIT_TIME)
    
    # Test routes for errors
    logger.info("Testing application routes")
    errors_detected = test_routes()
    
    if errors_detected:
        logger.warning("Errors detected in application routes")
        choice = input("Errors detected. Shutdown application for refactoring? (y/n): ")
        if choice.lower() == 'y':
            shutdown_application(process)
            logger.info("Application shut down for refactoring")
            return
    
    logger.info("No critical errors detected. Application is running.")
    logger.info("Press Ctrl+C to manually shut down the application")
    
    try:
        # Monitor the application
        monitor_application(process)
    except KeyboardInterrupt:
        logger.info("Manual shutdown requested")
        shutdown_application(process)
        logger.info("Application shut down manually")

if __name__ == "__main__":
    main() 