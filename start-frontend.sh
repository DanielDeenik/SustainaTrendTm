#!/bin/bash
set -e

# Kill any existing Vite processes
pkill -f "vite" || true

# Set environment variables for frontend
export NODE_ENV=development
export HOST=0.0.0.0
export PORT=3000

# Clean up any previous build artifacts
rm -rf dist || true

# Start the frontend development server with debug logging
exec npx vite --host 0.0.0.0 --port 3000 --force