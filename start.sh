#!/bin/bash
set -e

# Kill any existing processes
pkill -f "uvicorn" || true
pkill -f "node" || true

# Wait for ports to clear
sleep 2

# Create logs directory
mkdir -p logs

# Install dependencies if needed
npm install

# Build the SvelteKit app
echo "Building SvelteKit application..."
npm run build

# Start both servers
echo "Starting servers..."

# Start FastAPI server
cd backend
pip install fastapi uvicorn psycopg2-binary pydantic python-dotenv sqlalchemy
uvicorn main:app --host 0.0.0.0 --port 8000 --reload --log-level info > ../logs/backend.log 2>&1 &

# Return to root directory
cd ..

# Start SvelteKit server
echo "Starting SvelteKit server..."
PORT=3000 NODE_ENV=development node build > logs/frontend.log 2>&1 &

# Wait for servers to start
echo "Waiting for servers to start..."
sleep 5

# Keep script running
wait