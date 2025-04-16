#!/usr/bin/env python
"""
WSGI entry point for the SustainaTrend™ Intelligence Platform.
"""
from src.frontend.refactored.app import create_app

# Create the application instance
application = create_app()

if __name__ == '__main__':
    application.run() 