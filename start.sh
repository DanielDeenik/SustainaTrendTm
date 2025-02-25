#!/bin/bash
set -e

# Kill any existing processes
pkill -f "node" || true
pkill -f "uvicorn" || true
pkill -f "flask" || true

# Create logs directory
mkdir -p logs

# Wait for port function
wait_for_port() {
  local port=$1
  local timeout=${2:-30}
  local count=0

  echo "Waiting for port $port..."
  while ! nc -z localhost $port; do
    if [ $count -ge $timeout ]; then
      echo "Timeout waiting for port $port"
      return 1
    fi
    sleep 1
    count=$((count + 1))
  done
  echo "Port $port is available"
}

# Start Flask app
echo "Starting Flask application..."
cd ../
chmod +x start-flask.sh
./start-flask.sh > logs/flask.log 2>&1 &
FLASK_PID=$!

# Wait for Flask to be ready
wait_for_port 5000 || {
  echo "Flask server failed to start"
  cat logs/flask.log
  exit 1
}

echo "All services started successfully"
wait