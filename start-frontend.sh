#!/bin/bash
set -e

# Kill any existing Vite processes
pkill -f "vite" || true

# Set environment variables for frontend
export NODE_ENV=production
export HOST=0.0.0.0
export PORT=3000

# Clean up any previous build artifacts
rm -rf build || true

# Rebuild the SvelteKit application
npm run build

# Start the SvelteKit server
exec node build/index.js