#!/bin/bash

# Kill any existing process on ports (using pkill instead of lsof)
pkill -f "uvicorn main:app" || true
pkill -f "vite" || true

# Wait a moment for ports to clear
sleep 5

# Start FastAPI backend
cd backend && ./start.sh &

# Wait for backend to start
sleep 10

# Start the SvelteKit application with proper environment variables
echo "Starting SvelteKit application..."
export VITE_BACKEND_URL="http://localhost:8000" \
NODE_ENV=development \
ORIGIN=http://localhost:3000 \
HOST=0.0.0.0 \
PORT=3000

cd .. && vite dev --host 0.0.0.0 --port 3000