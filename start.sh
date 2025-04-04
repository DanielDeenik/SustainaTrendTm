#!/bin/bash
# SustainaTrend Intelligence Platform - Consolidated Startup Script
# This is the primary entry point for the platform

echo "Starting SustainaTrend Intelligence Platform..."

# Create logs directory if it doesn't exist
mkdir -p logs

# Terminate any existing processes on port 5000
EXISTING_PID=$(lsof -t -i:5000 2>/dev/null)
if [ ! -z "$EXISTING_PID" ]; then
    echo "Port 5000 is in use by process $EXISTING_PID. Terminating..."
    kill -15 $EXISTING_PID 2>/dev/null || kill -9 $EXISTING_PID 2>/dev/null
    sleep 2
fi

# Set environment variables
export FLASK_ENV=development
export FLASK_DEBUG=1
export HOST="0.0.0.0"
export PORT="5000"
export PYTHONUNBUFFERED=1

echo "Starting consolidated application on ${HOST}:${PORT}..."
python consolidated_app.py 2>&1 | tee logs/app.log
