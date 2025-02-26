#!/bin/bash
set -e

echo "Preparing Sustainability Dashboard..."

# Create logs directory if it doesn't exist
mkdir -p logs

# Kill any existing processes using port 5000 (in a Replit-friendly way)
pkill -f "port 5000" || true
pkill -f "flask" || true
pkill -f "redis-server" || true

# Install Python dependencies
python -m pip install flask==2.3.3 dash==2.9.3 pandas redis flask-caching plotly dash-bootstrap-components gunicorn

# Set environment variables
export FLASK_APP=app.py
export FLASK_ENV=development
export FLASK_DEBUG=1
export REDIS_URL="redis://localhost:6379/0"

# Start Redis server
redis-server --daemonize yes --logfile logs/redis.log \
    --maxmemory 256mb \
    --maxmemory-policy allkeys-lru

# Create directories if they don't exist
mkdir -p static
mkdir -p templates

echo "Starting Sustainability Dashboard on port 5000..."
exec python app.py