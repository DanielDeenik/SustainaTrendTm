#!/bin/bash
set -e

# Kill any existing processes
pkill -f "node" || true
pkill -f "uvicorn" || true

# Wait for ports to clear
sleep 2

echo "Installing dependencies..."
npm install

echo "Building SvelteKit application..."
npm run build

echo "Starting services..."

# Start FastAPI backend
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload > ../logs/backend.log 2>&1 &

# Return to root and start SvelteKit
cd ..
node build > logs/frontend.log 2>&1 &

# Keep script running
wait