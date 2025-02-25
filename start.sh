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

# Wait for port function
wait_for_port() {
  local port=$1
  local timeout=${2:-30}
  local count=0

  echo "Waiting for port $port..."
  while ! nc -z localhost $port; do
    if [ $count -ge $timeout ]; then
      echo "Timeout waiting for port $port"
      return 1
    fi
    sleep 1
    count=$((count + 1))
  done
  echo "Port $port is available"
}

# Start FastAPI backend
cd backend
chmod +x start.sh
./start.sh > ../logs/backend.log 2>&1 &
BACKEND_PID=$!

# Wait for backend to be ready
wait_for_port 8000 || {
  echo "Backend failed to start"
  cat ../logs/backend.log
  exit 1
}

# Return to root directory
cd ..

# Start Vite dev server
npx vite --host 0.0.0.0 --port 3000 > logs/frontend.log 2>&1 &
FRONTEND_PID=$!

# Wait for frontend to be ready
wait_for_port 3000 || {
  echo "Frontend failed to start"
  cat logs/frontend.log
  exit 1
}

echo "All services started successfully"
wait