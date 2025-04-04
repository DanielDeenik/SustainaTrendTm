#!/usr/bin/env python3
"""
Standalone script to run the Flask frontend
"""
import os
import sys

def run_flask():
    """Run the Flask frontend directly"""
    print("Starting Flask frontend...")
    
    # Set the Python path to include the frontend directory
    frontend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend")
    sys.path.insert(0, frontend_dir)
    
    # Change to the frontend directory
    os.chdir(frontend_dir)
    
    # Set environment variables
    os.environ['BACKEND_URL'] = 'http://localhost:8000'
    
    # Print environment variables for debugging
    print("\nEnvironment variables:")
    print(f"BACKEND_URL: {os.getenv('BACKEND_URL')}")
    print(f"FLASK_DEBUG: {os.getenv('FLASK_DEBUG', 'Not set, using default')}")
    
    # Import app from the frontend directory
    from app import app
    
    # Run the Flask application
    print("\nStarting Flask server on port 5000...")
    app.run(host="0.0.0.0", port=5000, debug=True)

if __name__ == "__main__":
    run_flask()
