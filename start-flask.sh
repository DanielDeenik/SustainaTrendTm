#!/bin/bash
set -e

# Kill any existing Flask processes
pkill -f "flask" || true

# Set environment variables
export FLASK_APP=app.py
export FLASK_ENV=development
export FLASK_DEBUG=1

# Install Python dependencies if not already installed
pip install flask flask-sqlalchemy psycopg2-binary python-dotenv

# Start Flask server
exec python -m flask run --host=0.0.0.0 --port=5000
