#!/bin/bash

# Kill any existing process on ports (using pkill instead of lsof)
pkill -f "uvicorn main:app" || true
pkill -f "vite" || true

# Wait a moment for ports to clear
sleep 5

# Start FastAPI backend
cd backend && ./start.sh &
backend_pid=$!

# Wait for backend to be ready - check port 8000
echo "Waiting for backend to be ready..."
timeout=30
counter=0
while ! nc -z localhost 8000; do
  if [ $counter -eq $timeout ]; then
    echo "Backend failed to start within $timeout seconds"
    exit 1
  fi
  counter=$((counter+1))
  sleep 1
done
echo "Backend is ready!"

# Start the SvelteKit application with proper environment variables
echo "Starting SvelteKit application..."
cd ..
export VITE_BACKEND_URL="http://localhost:8000" \
NODE_ENV=development \
ORIGIN=http://localhost:3000 \
HOST=0.0.0.0 \
PORT=3000

# Use exec to replace the shell with the final command
exec NODE_OPTIONS="--max-old-space-size=512" vite dev --host 0.0.0.0 --port 3000 --force