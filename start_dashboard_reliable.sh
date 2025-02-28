#!/bin/bash
set -e

echo "Starting Sustainability Dashboard with reliable port handling..."

# Check if psutil is installed, install if needed
python3 -c "import psutil" 2>/dev/null || pip install psutil

# Run our reliable starter script
python3 frontend/start_reliable.py

# This script should not exit normally as the Python script keeps running
echo "Flask application has stopped."
