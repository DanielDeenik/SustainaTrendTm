#!/bin/bash
set -e

# Set environment variables for frontend
export VITE_BACKEND_URL="http://0.0.0.0:8000"
export NODE_ENV=development
export ORIGIN=http://0.0.0.0:3000
export HOST=0.0.0.0
export PORT=3000

# Start the frontend development server 
exec npx vite dev --host 0.0.0.0 --port 3000