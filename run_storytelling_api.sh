#!/bin/bash
set -e

echo "Starting FastAPI Storytelling API with reliable port handling..."

# Check if psutil is installed, install if needed
python3 -c "import psutil" 2>/dev/null || pip install psutil

# Copy port_manager.py to the correct location if it's not there
if [ ! -f backend/port_manager.py ]; then
  cp frontend/port_manager.py backend/ 2>/dev/null || cp port_manager.py backend/ 2>/dev/null || true
fi

# Change to the backend directory
cd backend

# Use our port manager to run the API on port 8080 reliably
python3 port_manager.py --port 8080 --run "python3 ../run-storytelling-api.py"

# This script should not exit normally as the Python script keeps running
echo "FastAPI application has stopped."
