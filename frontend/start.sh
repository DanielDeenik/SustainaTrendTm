#!/bin/bash
set -e

# Create logs directory if it doesn't exist
mkdir -p logs

# Kill any existing processes to avoid port conflicts
pkill -f "gunicorn" || true
pkill -f "redis-server" || true

# Install Python dependencies
pip install --quiet flask dash dash-bootstrap-components pandas gunicorn redis flask-caching plotly

# Set environment variables
export FLASK_APP=app.py
export FLASK_ENV=development
export FLASK_DEBUG=1
export REDIS_URL="redis://localhost:6379/0"

# Start Redis server
redis-server --daemonize yes --logfile logs/redis.log \
    --maxmemory 256mb \
    --maxmemory-policy allkeys-lru

# Make the script executable
chmod +x app.py

# Start Flask server with Gunicorn
echo "Starting Flask server with Gunicorn on port 5001..."
exec gunicorn "app:app" \
    --worker-class sync \
    --workers 4 \
    --bind 0.0.0.0:5001 \
    --access-logfile logs/access.log \
    --error-logfile logs/error.log \
    --reload \
    --timeout 120