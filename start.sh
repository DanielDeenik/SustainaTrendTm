#!/bin/bash
set -e

# Kill any existing processes
pkill -f "node" || true
pkill -f "uvicorn" || true
pkill -f "flask" || true

# Create logs directory
mkdir -p logs

# Make scripts executable
chmod +x start-flask.sh
chmod +x app.py

# Start Flask app directly
echo "Starting Flask application..."
./start-flask.sh