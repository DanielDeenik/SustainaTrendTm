#!/bin/bash
set -e

# Kill any existing uvicorn processes
pkill -f "uvicorn main:app" || true

# Wait for port to be available
sleep 2

# Set proper file permissions
chmod +x main.py

# Install Python dependencies if not already installed
pip install fastapi uvicorn psycopg2-binary pydantic python-dotenv sqlalchemy

# Start the FastAPI server with proper host binding and logging
exec uvicorn main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --reload \
  --workers 1 \
  --log-level info \
  --reload-dir /home/runner/workspace/backend