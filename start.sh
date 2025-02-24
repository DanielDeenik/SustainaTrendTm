#!/bin/bash
set -e

# Kill any existing processes
pkill -f "node" || true
pkill -f "uvicorn" || true

# Create logs directory
mkdir -p logs

# Install dependencies and ensure proper ESM setup
echo "Installing dependencies..."
npm install

# Build the SvelteKit application with proper ESM support
echo "Building SvelteKit application..."
NODE_ENV=production NODE_OPTIONS="--experimental-modules --es-module-specifier-resolution=node" npm run build

# Start FastAPI backend
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload > ../logs/backend.log 2>&1 &

# Return to root and start SvelteKit with ESM support
cd ..
export PORT=3000
NODE_OPTIONS="--experimental-modules --es-module-specifier-resolution=node" node build > logs/frontend.log 2>&1 &

# Wait for both services
wait