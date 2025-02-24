#!/bin/bash
set -e

# Kill any existing Vite processes
pkill -f "vite" || true

# Set environment variables for frontend
export VITE_BACKEND_URL="http://0.0.0.0:8000"
export NODE_ENV=development
export ORIGIN=http://0.0.0.0:3000
export HOST=0.0.0.0
export PORT=3000

# Start the frontend development server with debug logging
exec npx vite --host 0.0.0.0 --port 3000 --debug