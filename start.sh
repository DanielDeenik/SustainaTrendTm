#!/bin/bash
set -e

# Kill any existing processes on ports
pkill -f "uvicorn main:app" || true
pkill -f "vite" || true

# Wait for ports to clear
sleep 2

# Create logs directory if it doesn't exist
mkdir -p logs

# Ensure backend start.sh is executable
chmod +x backend/start.sh

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

# Navigate back to root directory
cd ..

# Set environment variables for frontend
export VITE_BACKEND_URL="http://localhost:8000"
export NODE_ENV=development
export ORIGIN=http://localhost:3000
export HOST=0.0.0.0
export PORT=3000

# Start the frontend application with proper logging
npm run dev -- --host 0.0.0.0 --port 3000 > logs/frontend.log 2>&1