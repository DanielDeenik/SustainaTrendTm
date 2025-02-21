#!/bin/bash

# Kill any existing process on port 8000 (using pkill instead of lsof)
pkill -f "uvicorn main:app" || true

# Wait a moment for ports to clear
sleep 2

# Start FastAPI backend
cd backend && ./start.sh &

# Wait for backend to start
sleep 5

# Start the SvelteKit application
echo "Starting SvelteKit application..."
NODE_OPTIONS="--experimental-modules" \
VITE_BACKEND_URL="http://localhost:8000" \
NODE_ENV=development \
ORIGIN=http://localhost:3000 \
HOST=0.0.0.0 \
PORT=3000 \
vite dev --host 0.0.0.0 --port 3000