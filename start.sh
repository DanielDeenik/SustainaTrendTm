#!/bin/bash
set -e

# Kill any existing processes on ports
pkill -f "uvicorn main:app" || true
pkill -f "vite" || true
pkill -f "node" || true

# Wait for ports to clear
sleep 2

# Create logs directory if it doesn't exist
mkdir -p logs

# Ensure backend start.sh is executable
chmod +x backend/start.sh
chmod +x backend/main.py

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

# Set environment variables for frontend
export VITE_BACKEND_URL="http://localhost:8000"
export NODE_ENV=development
export ORIGIN=http://localhost:3000
export HOST=0.0.0.0

# Return to project root and start the dev server
cd /home/runner/workspace
npx vite dev --host 0.0.0.0 --port 3000