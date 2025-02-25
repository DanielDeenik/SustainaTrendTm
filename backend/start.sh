#!/bin/bash
set -e

echo "Starting FastAPI server..."

# Kill any existing uvicorn processes
pkill -f "uvicorn" || true

# Create logs directory if it doesn't exist
mkdir -p logs

# Install Python dependencies if not already installed
pip install --quiet fastapi uvicorn psycopg2-binary pydantic python-dotenv sqlalchemy

# Set PYTHONPATH to include the project root
cd ..
export PYTHONPATH="${PWD}"

# Change to backend directory and start the FastAPI server
cd backend

# Start server and wait for it to be ready
uvicorn main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --reload \
  --workers 1 \
  --log-level info \
  --access-log &

# Wait for the server to be ready
echo "Waiting for FastAPI server to be ready..."
until $(curl --output /dev/null --silent --fail http://localhost:8000/health); do
    echo "Waiting for server to be ready..."
    sleep 2
done

echo "FastAPI server is ready!"

# Keep the script running
wait