#!/bin/bash
set -e

# Kill any existing processes
pkill -f "node" || true
pkill -f "uvicorn" || true
pkill -f "flask" || true

# Create logs directory
mkdir -p logs

# Start Flask app
echo "Starting Flask application..."
chmod +x start-flask.sh
./start-flask.sh > logs/flask.log 2>&1 &
FLASK_PID=$!

# Wait until port 5000 is available
echo "Waiting for Flask server to start..."
until $(curl --output /dev/null --silent --head --fail http://localhost:5000); do
    if ! ps -p $FLASK_PID > /dev/null; then
        echo "Flask server failed to start. Check logs at logs/flask.log"
        exit 1
    fi
    sleep 1
done

echo "Flask server is running!"
wait $FLASK_PID