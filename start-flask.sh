#!/bin/bash
set -e

# Install Python dependencies
pip install --quiet flask flask-sqlalchemy psycopg2-binary python-dotenv redis flask-caching celery flask-socketio eventlet gunicorn

# Set environment variables
export FLASK_APP=app.py
export FLASK_ENV=development
export FLASK_DEBUG=1
export REDIS_URL="redis://localhost:6379/0"

# Start Redis server in the background
redis-server --daemonize yes

# Give execute permission to app.py
chmod +x app.py

# Start Flask server with Gunicorn
echo "Starting Flask server with Gunicorn on port 5000..."
exec gunicorn --config gunicorn.conf.py --worker-class eventlet -w 4 "app:app"