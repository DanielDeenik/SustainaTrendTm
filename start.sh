#!/bin/bash
set -e

# Kill any existing processes
pkill -f "node" || true
pkill -f "uvicorn" || true
pkill -f "flask" || true
pkill -f "port 5001" || true

# Create logs directory
mkdir -p logs

# Start Flask dashboard
echo "Starting Flask dashboard..."
cd frontend && ./start.sh