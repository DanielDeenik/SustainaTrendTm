#!/bin/bash

# Start the SvelteKit frontend
echo "Starting SvelteKit frontend..."
NODE_OPTIONS="--experimental-modules" \
VITE_SVELTEKIT_HOST="0.0.0.0" \
VITE_SVELTEKIT_ALLOW_ALL_HOSTS=true \
npx vite dev --host 0.0.0.0 --port 3001 &

# Wait a moment to ensure frontend starts
sleep 2

# Start the FastAPI backend
echo "Starting FastAPI backend..."
cd backend && python main.py &

# Wait for both servers to be ready
wait