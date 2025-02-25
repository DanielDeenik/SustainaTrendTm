#!/bin/bash
set -e

# Create logs directory if it doesn't exist
mkdir -p logs

# Kill any existing processes
pkill -f "flask" || true
pkill -f "redis-server" || true

# Install Python dependencies
pip install flask dash pandas gunicorn redis flask-caching plotly dash-bootstrap-components

# Set environment variables
export FLASK_APP=app.py
export FLASK_ENV=development
export FLASK_DEBUG=1

# Start Redis server
redis-server --daemonize yes --logfile logs/redis.log \
    --maxmemory 256mb \
    --maxmemory-policy allkeys-lru

echo "Starting Flask application on port 5001..."
python app.py