"""
Run script for the SustainaTrend™ Intelligence Platform.
"""
import os
import sys

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, project_root)

from src.frontend.refactored.app import run_app

if __name__ == '__main__':
    # Run the application
    run_app() 