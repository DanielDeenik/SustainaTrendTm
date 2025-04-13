#!/usr/bin/env python
"""
Application Launch Script

This script automatically launches the SustainaTrend application with proper initialization
and database setup.
"""

import os
import sys
import subprocess
import logging
import time
from pathlib import Path

# Add src directory to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
src_path = os.path.join(project_root, 'src')
sys.path.insert(0, src_path)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/launch.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def check_mongodb():
    """Check if MongoDB is running."""
    try:
        import pymongo
        client = pymongo.MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=5000)
        client.server_info()
        logger.info("MongoDB is running")
        return True
    except Exception as e:
        logger.error(f"MongoDB is not running: {e}")
        logger.error("Please install and start MongoDB before launching the application")
        logger.error("Installation instructions: https://www.mongodb.com/try/download/community")
        return False

def initialize_database():
    """Initialize the database using init_db.py script."""
    try:
        logger.info("Initializing database...")
        init_script = Path(__file__).parent / "init_db.py"
        result = subprocess.run([sys.executable, str(init_script)], capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info("Database initialized successfully")
            return True
        else:
            logger.error(f"Database initialization failed: {result.stderr}")
            return False
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        return False

def start_application():
    """Start the Flask application."""
    try:
        logger.info("Starting application...")
        app_script = Path(__file__).parent.parent / "app.py"
        env = os.environ.copy()
        env["PYTHONPATH"] = src_path + os.pathsep + env.get("PYTHONPATH", "")
        
        process = subprocess.Popen(
            [sys.executable, str(app_script)],
            env=env,
            cwd=project_root  # Set working directory to project root
        )
        
        # Wait for the application to start
        time.sleep(5)
        
        if process.poll() is None:
            logger.info("Application started successfully")
            return process
        else:
            logger.error("Application failed to start")
            return None
    except Exception as e:
        logger.error(f"Error starting application: {e}")
        return None

def main():
    """Main function to launch the application."""
    try:
        # Create logs directory if it doesn't exist
        os.makedirs('logs', exist_ok=True)
        
        # Check if MongoDB is running
        if not check_mongodb():
            logger.error("MongoDB is required to run the application")
            sys.exit(1)
        
        # Initialize database
        if not initialize_database():
            logger.error("Database initialization failed")
            sys.exit(1)
        
        # Start application
        process = start_application()
        if process is None:
            logger.error("Failed to start application")
            sys.exit(1)
        
        # Keep the script running
        try:
            process.wait()
        except KeyboardInterrupt:
            logger.info("Shutting down application...")
            process.terminate()
            process.wait()
            logger.info("Application shut down successfully")
        
    except Exception as e:
        logger.error(f"Error launching application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 