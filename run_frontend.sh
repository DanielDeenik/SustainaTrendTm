#!/bin/bash
set -e

echo "Starting Flask frontend on port 5000..."
cd frontend

# Set backend URL
export BACKEND_URL="http://localhost:8000"
echo "Using BACKEND_URL: $BACKEND_URL"

# Check if psutil is installed, install if needed
python3 -c "import psutil" 2>/dev/null || pip install psutil

# Make sure port_manager.py is available
if [ ! -f port_manager.py ]; then
  cp ../port_manager.py ./ 2>/dev/null || echo "Warning: port_manager.py not found"
fi

# Use our port manager to run Flask reliably on port 5000
python3 port_manager.py --flask direct_app.py