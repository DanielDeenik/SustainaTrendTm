#!/bin/bash
set -e

echo "Starting FastAPI server..."

# Kill any existing uvicorn processes
pkill -f "uvicorn" || true

# Wait for port 8000 to be available
echo "Waiting for port 8000 to be available..."
while lsof -i :8000 >/dev/null 2>&1; do
    echo "Port 8000 is still in use, waiting..."
    sleep 2
done

# Create logs directory if it doesn't exist
mkdir -p logs

# Install Python dependencies if not already installed
pip install --quiet fastapi uvicorn psycopg2-binary pydantic python-dotenv sqlalchemy

# Set PYTHONPATH to include the project root
cd "$(dirname "$0")/.."
export PYTHONPATH="${PWD}:${PYTHONPATH}"

# Start the FastAPI server
cd backend
exec uvicorn main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --reload \
  --workers 1 \
  --log-level info \
  --reload-dir . \
  --access-log