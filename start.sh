#!/bin/bash

# Start the SvelteKit application
echo "Starting SvelteKit application..."
NODE_OPTIONS="--experimental-modules" \
VITE_SVELTEKIT_HOST="0.0.0.0" \
VITE_SVELTEKIT_ALLOW_ALL_HOSTS=true \
npm run dev -- --host 0.0.0.0 --port 3000