#!/bin/bash
set -e

# Create logs directory if it doesn't exist
mkdir -p logs

# Kill any existing processes to avoid port conflicts
pkill -f "gunicorn" || true
pkill -f "redis-server" || true

# Install Python dependencies
pip install --quiet flask flask-sqlalchemy psycopg2-binary python-dotenv redis flask-caching \
    celery flask-socketio eventlet gunicorn dash dash-bootstrap-components pandas plotly

# Set environment variables
export FLASK_APP=app.py
export FLASK_ENV=development
export FLASK_DEBUG=1
export REDIS_URL="redis://localhost:6379/0"

# Start Redis server with proper configuration
redis-server --daemonize yes --logfile logs/redis.log \
    --maxmemory 256mb \
    --maxmemory-policy allkeys-lru

# Start Flask server with Gunicorn
echo "Starting Flask server with Gunicorn on port 5000..."
exec gunicorn "app:server" \
    --config gunicorn.conf.py \
    --worker-class eventlet \
    --workers 4 \
    --bind 0.0.0.0:5000 \
    --access-logfile logs/access.log \
    --error-logfile logs/error.log \
    --reload \
    --timeout 120