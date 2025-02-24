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

# Ensure scripts are executable
chmod +x backend/start.sh
chmod +x backend/main.py
chmod +x start-frontend.sh

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

# Return to project root and start the frontend
cd /home/runner/workspace
./start-frontend.sh > logs/frontend.log 2>&1 &
frontend_pid=$!

# Wait for frontend to be ready
echo "Waiting for frontend to be ready..."
counter=0
while ! nc -z localhost 3000; do
  if [ $counter -eq $timeout ]; then
    echo "Frontend failed to start within $timeout seconds"
    cat logs/frontend.log
    exit 1
  fi
  counter=$((counter+1))
  sleep 1
done
echo "Frontend is ready!"

# Keep the script running
wait $backend_pid $frontend_pid