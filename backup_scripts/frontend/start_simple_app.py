#!/usr/bin/env python
"""
Simple starter script for the SustainaTrend™ Intelligence Platform demo
"""

import os
import sys
import logging
from simple_app import app

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info("Starting SustainaTrend™ Intelligence Platform Demo")
    logger.info(f"Current working directory: {os.getcwd()}")
    logger.info(f"Python executable: {sys.executable}")
    logger.info(f"Python path: {sys.path}")
    
    # Get port
    port = int(os.environ.get('PORT', 5000))
    
    # Run the app
    app.run(host="0.0.0.0", port=port, debug=True)