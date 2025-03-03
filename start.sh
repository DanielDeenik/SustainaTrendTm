#!/bin/bash

echo "Starting Sustainability Intelligence Platform..."

# Create logs directory
mkdir -p logs

# Function to check if port is already in use
check_port() {
  local port=$1
  if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null ; then
    echo "Port $port is already in use."
    return 0
  else
    return 1
  fi
}

# Function to gracefully terminate processes
terminate_processes() {
  echo "Cleaning up existing processes..."
  # Kill processes in a Replit-friendly way
  for process in "python.*app.py" "flask" "port 5000" "redis-server" "gunicorn"; do
    pids=$(pgrep -f "$process" 2>/dev/null || true)
    if [ -n "$pids" ]; then
      echo "Terminating $process processes: $pids"
      for pid in $pids; do
        # Try graceful termination first
        kill -15 $pid 2>/dev/null || true
        # Wait a bit
        sleep 1
        # Force kill if still running
        kill -9 $pid 2>/dev/null || true
      done
    fi
  done
  sleep 2
}

# Clean up existing processes
terminate_processes

# Make the frontend start script executable
chmod +x frontend/start.sh

# Check if port 5000 is free
if check_port 5000; then
  echo "Warning: Port 5000 is still in use. Attempting to free it..."
  fuser -k 5000/tcp 2>/dev/null || true
  sleep 2
fi

# Start Flask dashboard
echo "Starting Flask dashboard on port 5000..."
cd frontend && ./start.sh &

# Wait for port to become available
echo "Waiting for server to start on port 5000..."
timeout=60
while [ $timeout -gt 0 ]; do
  if curl -s http://localhost:5000 > /dev/null 2>&1; then
    echo "Server is up and running on port 5000!"
    break
  fi
  sleep 1
  timeout=$((timeout-1))
done

if [ $timeout -eq 0 ]; then
  echo "Warning: Timed out waiting for server to start, but continuing anyway..."
fi

# Keep the script running
wait