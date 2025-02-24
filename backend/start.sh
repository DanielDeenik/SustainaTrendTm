#!/bin/bash
set -e

echo "Starting FastAPI server..."

# Kill any existing uvicorn processes
pkill -f "uvicorn backend.main:app" || true

# Wait for port to be available
echo "Waiting for port 8000 to be available..."
while lsof -i :8000 >/dev/null 2>&1; do
    echo "Port 8000 is still in use, waiting..."
    sleep 2
done

# Create logs directory if it doesn't exist
mkdir -p logs

# Build the frontend first
echo "Building frontend..."
npx vite build

# Set proper permissions
chmod +x main.py

# Add the project root to PYTHONPATH
export PYTHONPATH="/home/runner/workspace:${PYTHONPATH}"

# Install Python dependencies if not already installed
pip install fastapi uvicorn psycopg2-binary pydantic python-dotenv sqlalchemy

# Start the FastAPI server with proper host binding and logging
exec uvicorn backend.main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --reload \
  --workers 1 \
  --log-level info \
  --reload-dir /home/runner/workspace/backend \
  --access-log