#!/bin/bash
set -e

# Kill any existing processes on ports
pkill -f "uvicorn backend.main:app" || true
pkill -f "vite" || true
pkill -f "node" || true

# Wait for ports to clear
sleep 2

# Create logs directory if it doesn't exist
mkdir -p logs

# Build the frontend first
echo "Building frontend..."
npx vite build

# Ensure scripts are executable
chmod +x backend/start.sh
chmod +x backend/main.py

# Add the project root to PYTHONPATH
export PYTHONPATH="/home/runner/workspace:${PYTHONPATH}"

# Start FastAPI backend with proper logging
cd backend && ./start.sh > ../logs/backend.log 2>&1 &
backend_pid=$!

# Wait for backend to be ready - check port 8000
echo "Waiting for backend to be ready..."
timeout=30
counter=0
while ! nc -z localhost 8000; do
  if [ $counter -eq $timeout ]; then
    echo "Backend failed to start within $timeout seconds"
    cat ../logs/backend.log
    exit 1
  fi
  counter=$((counter+1))
  sleep 1
done
echo "Backend is ready!"

# Keep the script running
wait $backend_pid