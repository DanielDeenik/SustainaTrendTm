#!/usr/bin/env python
"""
SustainaTrend™ Intelligence Platform - Main Entry Point

This script serves as the main entry point for the SustainaTrend™ application.
It imports and calls the run_app() function from the refactored app module.
"""

import os
import sys
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Configure basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/app.log')
    ]
)

logger = logging.getLogger(__name__)

def main():
    """Main entry point for the SustainaTrend™ application."""
    try:
        logger.info("Starting SustainaTrend™ Intelligence Platform")
        
        # Import the run_app function from the refactored app
        from src.frontend.refactored.app import run_app
        
        # Run the application
        run_app()
        
    except Exception as e:
        logger.error(f"Error starting SustainaTrend™: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main() 