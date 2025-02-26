#!/bin/bash
set -e

# Create logs directory if it doesn't exist
mkdir -p logs

# Kill any existing processes using port 5001
fuser -k 5001/tcp || true
pkill -f "port 5001" || true
pkill -f "flask" || true
pkill -f "redis-server" || true

# Install Python dependencies
pip install flask dash pandas gunicorn redis flask-caching plotly dash-bootstrap-components

# Set environment variables
export FLASK_APP=app.py
export FLASK_ENV=development
export FLASK_DEBUG=1
export REDIS_URL="redis://localhost:6379/0"

# Start Redis server
redis-server --daemonize yes --logfile logs/redis.log \
    --maxmemory 256mb \
    --maxmemory-policy allkeys-lru

# Create styles.css if it doesn't exist
mkdir -p static
cat > static/styles.css <<EOF
body {
    font-family: Arial, sans-serif;
    margin: 0;
    padding: 0;
}
nav {
    background-color: #333;
    color: white;
    padding: 1rem;
}
nav ul {
    list-style-type: none;
    margin: 0;
    padding: 0;
    display: flex;
}
nav li {
    margin-right: 1rem;
}
nav a {
    color: white;
    text-decoration: none;
}
#content {
    padding: 1rem;
}
EOF

echo "Starting Flask application on port 5001..."
python app.py