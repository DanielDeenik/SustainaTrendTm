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
chmod +x start.sh
./start.sh > ../logs/backend.log 2>&1 &
BACKEND_PID=$!

# Return to root directory
cd ..

# Start Vite dev server directly
npx vite --host 0.0.0.0 --port 3000 > logs/frontend.log 2>&1 &
FRONTEND_PID=$!

# Wait for services to be ready
echo "Waiting for services to start..."
sleep 5

# Check if services are running
if ! ps -p $BACKEND_PID > /dev/null; then
    echo "Error: Backend failed to start"
    cat logs/backend.log
    exit 1
fi

if ! ps -p $FRONTEND_PID > /dev/null; then
    echo "Error: Frontend failed to start"
    cat logs/frontend.log
    exit 1
fi

echo "All services started successfully"
wait