#!/bin/bash
set -e

echo "Starting Sustainability Intelligence Platform..."

# Create logs directory if it doesn't exist
mkdir -p logs

# Kill any existing processes in a Replit-friendly way
pkill -f "python" || true
pkill -f "flask" || true
pkill -f "port 5000" || true
pkill -f "redis-server" || true
pkill -f "gunicorn" || true
pkill -f "uvicorn" || true

# Make scripts executable
chmod +x frontend/start.sh
chmod +x backend/start.sh
chmod +x backend/seed_database.py

# Set environment variable for FastAPI backend URL
export BACKEND_URL="http://localhost:8000"

# Seed the database with sample metrics
echo "Seeding database with sample metrics..."
cd backend
python seed_database.py
cd ..

# Start FastAPI backend in background
echo "Starting FastAPI backend on port 8000..."
cd backend
./start.sh &
FASTAPI_PID=$!
cd ..

# Wait for FastAPI to be ready
echo "Waiting for FastAPI backend to be ready..."
until $(curl --output /dev/null --silent --fail http://localhost:8000/health); do
    if ! ps -p $FASTAPI_PID > /dev/null; then
        echo "Backend server failed to start. Check logs at logs/backend.log"
        exit 1
    fi
    echo "Waiting for FastAPI backend to be ready..."
    sleep 2
done

echo "FastAPI backend is ready!"

# Start Flask dashboard
echo "Starting Flask frontend on port 5000..."
cd frontend
# Added environment variable to specify backend URL
BACKEND_URL="http://localhost:8000" ./start.sh