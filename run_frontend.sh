#!/bin/bash
set -e

echo "Starting Flask frontend on port 5001..."
cd frontend

# Set backend URL
export BACKEND_URL="http://localhost:8000"
echo "Using BACKEND_URL: $BACKEND_URL"

# Run Flask directly (on port 5001 to avoid conflicts)
python3 direct_app.py
