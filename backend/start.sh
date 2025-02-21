#!/bin/bash
# Install Python dependencies if needed
pip install fastapi uvicorn psycopg2-binary pydantic python-dotenv sqlalchemy

# Forcefully kill any existing uvicorn processes
pkill -f "uvicorn main:app" || true

# Wait longer to ensure port is freed
sleep 5

# Start the FastAPI server with proper host binding and minimal workers
uvicorn main:app --host 0.0.0.0 --port 8000 --reload --workers 1 --reload-dir /home/runner/workspace/backend