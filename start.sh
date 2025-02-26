#!/bin/bash
set -e

echo "Starting Sustainability Intelligence Platform..."

# Kill any existing processes in a Replit-friendly way
pkill -f "python" || true
pkill -f "flask" || true
pkill -f "port 5000" || true
pkill -f "redis-server" || true
pkill -f "gunicorn" || true

# Create logs directory
mkdir -p logs

# Make the frontend start script executable
chmod +x frontend/start.sh

# Start Flask dashboard with Gunicorn
echo "Starting Flask dashboard on port 5000 with Gunicorn..."
cd frontend && ./start.sh