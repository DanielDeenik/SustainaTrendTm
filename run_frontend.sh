#!/bin/bash
set -e

echo "Starting Flask frontend on port 5000..."
cd frontend

# Set backend URL
export BACKEND_URL="http://localhost:8000"
echo "Using BACKEND_URL: $BACKEND_URL"

# Check if psutil is installed, install if needed
python3 -c "import psutil" 2>/dev/null || pip install psutil

# Run the reliable starter script that handles port conflicts
python3 start_reliable.py