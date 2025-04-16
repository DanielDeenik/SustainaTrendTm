"""
Auto-start script for SustainaTrend™ Intelligence Platform.
This script handles automatic application startup and browser launch.
"""

import os
import sys
import time
import webbrowser
import subprocess
from threading import Thread
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def open_browser():
    """Open Google Chrome to the application URL."""
    # Wait for the server to start
    time.sleep(2)
    url = "http://127.0.0.1:5000"
    logger.info(f"Opening Chrome at {url}")
    
    # Try to find Chrome in common installation paths
    chrome_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expanduser("~") + r"\AppData\Local\Google\Chrome\Application\chrome.exe"
    ]
    
    chrome_path = None
    for path in chrome_paths:
        if os.path.exists(path):
            chrome_path = path
            break
    
    if chrome_path:
        # Launch Chrome with the application URL
        subprocess.Popen([chrome_path, url])
        logger.info("Launched Chrome successfully")
    else:
        # Fallback to default browser if Chrome is not found
        logger.warning("Chrome not found, using default browser")
        webbrowser.open(url)

def start_application():
    """Start the Flask application."""
    try:
        # Load environment variables
        load_dotenv()
        
        # Update environment variables for Flask
        os.environ['FLASK_ENV'] = 'development'
        os.environ['FLASK_DEBUG'] = '1'
        os.environ['HOST'] = '0.0.0.0'  # Bind to all interfaces
        os.environ['PORT'] = '5000'
        
        # Start the browser in a separate thread
        browser_thread = Thread(target=open_browser)
        browser_thread.daemon = True
        browser_thread.start()
        
        # Start the Flask application
        logger.info("Starting SustainaTrend™ application...")
        
        # Import the application here to ensure environment variables are set
        from src.frontend.refactored.app import create_app
        app = create_app()
        app.run(host='0.0.0.0', port=5000, debug=True)
        
    except Exception as e:
        logger.error(f"Error starting application: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    start_application() 