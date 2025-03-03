#!/bin/bash

echo "Preparing Sustainability Dashboard..."

# Create logs directory if it doesn't exist
mkdir -p logs

# Function to check if port is available
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
  # Kill processes in a Replit-friendly way with more specific patterns
  for process in "port 5000" "flask" "python.*app.py" "python.*direct_app.py" "gunicorn"; do
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

# Check if port 5000 is still in use
if check_port 5000; then
  echo "Warning: Port 5000 is still in use after cleanup. Attempting to forcefully free it..."
  # Try using fuser to kill processes using port 5000
  fuser -k 5000/tcp 2>/dev/null || true
  sleep 2
fi

# Install Python dependencies with timeout and retry
echo "Installing required Python packages..."
attempt=1
max_attempts=3
while [ $attempt -le $max_attempts ]; do
  echo "Attempt $attempt of $max_attempts to install packages..."
  if timeout 60 python -m pip install flask==2.3.3 plotly pandas requests flask-caching google-generativeai==0.3.2 httpx==0.24.1; then
    echo "Packages installed successfully."
    break
  else
    echo "Package installation attempt $attempt failed."
    attempt=$((attempt+1))
    if [ $attempt -le $max_attempts ]; then
      echo "Retrying in 5 seconds..."
      sleep 5
    else
      echo "Warning: Failed to install packages after $max_attempts attempts. Continuing anyway..."
    fi
  fi
done

# Set environment variables
export FLASK_APP=app.py
export FLASK_ENV=development
export FLASK_DEBUG=1

# Create required directories
mkdir -p static
mkdir -p templates
mkdir -p logs

# Clear any existing log files to prevent them from growing too large
> logs/flask.log
> logs/error.log
> logs/access.log

echo "Starting Sustainability Dashboard on port 5000..."
# Use app.py which is our bridge to direct_app.py
# Add timeout for stability
python app.py 2>&1 | tee logs/flask.log