#!/bin/bash
set -e

# Kill any existing processes
pkill -f "node" || true
pkill -f "uvicorn" || true

# Create logs directory
mkdir -p logs

# Install dependencies
echo "Installing dependencies..."
npm install

# Start FastAPI backend
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload > ../logs/backend.log 2>&1 &

# Return to root and start Vite dev server
cd ..
npm run dev > logs/frontend.log 2>&1 &

# Wait for both services
wait