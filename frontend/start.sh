#!/bin/bash
set -e

echo "Preparing Sustainability Dashboard..."

# Create logs directory if it doesn't exist
mkdir -p logs

# Kill any existing processes using port 5000 (in a Replit-friendly way)
pkill -f "port 5000" || true
pkill -f "flask" || true
pkill -f "python app.py" || true
pkill -f "python direct_app.py" || true
pkill -f "gunicorn" || true

# Install Python dependencies if needed
python -m pip install flask==2.3.3 plotly pandas requests flask-caching

# Set environment variables
export FLASK_APP=app.py
export FLASK_ENV=development
export FLASK_DEBUG=1

# Create directories if they don't exist
mkdir -p static
mkdir -p templates

echo "Starting Sustainability Dashboard on port 5000..."
# Use app.py which is our bridge to direct_app.py
python app.py