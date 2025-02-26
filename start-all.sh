#!/bin/bash
set -e

echo "Starting Sustainability Intelligence Platform..."

# Create logs directory if it doesn't exist
mkdir -p logs

# Kill any existing processes in a Replit-friendly way
pkill -f "python" || true
pkill -f "flask" || true
pkill -f "port 5000" || true
pkill -f "port 8000" || true
pkill -f "redis-server" || true
pkill -f "gunicorn" || true
pkill -f "uvicorn" || true

# Make scripts executable
chmod +x frontend/start.sh
chmod +x backend/start.sh
chmod +x backend/seed_database.py

# Set environment variable for FastAPI backend URL
export BACKEND_URL="http://localhost:8000"

# Display database connection info (without sensitive values)
echo "Database configuration:"
echo "- DATABASE_URL exists: $(if [ -n "$DATABASE_URL" ]; then echo "yes"; else echo "no"; fi)"
echo "- PGDATABASE exists: $(if [ -n "$PGDATABASE" ]; then echo "yes"; else echo "no"; fi)"
echo "- PGUSER exists: $(if [ -n "$PGUSER" ]; then echo "yes"; else echo "no"; fi)"
echo "- PGHOST exists: $(if [ -n "$PGHOST" ]; then echo "yes"; else echo "no"; fi)"
echo "- PGPORT exists: $(if [ -n "$PGPORT" ]; then echo "yes"; else echo "no"; fi)"

# Try to create the PostgreSQL database if it doesn't exist
if [ -z "$DATABASE_URL" ] && [ -z "$PGDATABASE" ]; then
    echo "No database configuration found. Attempting to create a PostgreSQL database..."
    create_postgresql_database_tool
fi

# Seed the database with sample metrics but continue if it fails
echo "Seeding database with sample metrics..."
cd backend
python seed_database.py || echo "Note: Database seeding encountered issues. Continuing with startup anyway..."
cd ..

# Start FastAPI backend in background
echo "Starting FastAPI backend on port 8000..."
cd backend
./start.sh &
FASTAPI_PID=$!
cd ..

# Wait for FastAPI to be ready
echo "Waiting for FastAPI backend to be ready..."
MAX_RETRIES=10
RETRY_COUNT=0
until $(curl --output /dev/null --silent --head --fail http://localhost:8000/health); do
    if ! ps -p $FASTAPI_PID > /dev/null; then
        echo "Backend server failed to start. Check logs at logs/backend.log"
        exit 1
    fi

    RETRY_COUNT=$((RETRY_COUNT+1))
    if [ $RETRY_COUNT -ge $MAX_RETRIES ]; then
        echo "Warning: Backend health check timed out, but continuing with frontend startup..."
        break
    fi

    echo "Waiting for FastAPI backend to be ready (attempt $RETRY_COUNT/$MAX_RETRIES)..."
    sleep 2
done

echo "FastAPI backend is ready (or timeout occurred)!"

# Test API access
echo "Testing API access..."
curl -s http://localhost:8000/api/metrics | head -20

# Start Flask frontend
echo "Starting Flask frontend on port 5000..."
cd frontend

# Added environment variable to specify backend URL
BACKEND_URL="http://localhost:8000" ./start.sh &
FLASK_PID=$!
cd ..

# Wait for Flask to be ready
echo "Waiting for Flask frontend to be ready..."
MAX_RETRIES=10
RETRY_COUNT=0
until $(curl --output /dev/null --silent --head --fail http://localhost:5000); do
    if ! ps -p $FLASK_PID > /dev/null; then
        echo "Frontend server failed to start. Check logs."
        exit 1
    fi

    RETRY_COUNT=$((RETRY_COUNT+1))
    if [ $RETRY_COUNT -ge $MAX_RETRIES ]; then
        echo "Warning: Frontend health check timed out."
        break
    fi

    echo "Waiting for Flask frontend to be ready (attempt $RETRY_COUNT/$MAX_RETRIES)..."
    sleep 2
done

echo "Flask frontend is ready (or timeout occurred)!"
echo "Services are running. Press Ctrl+C to stop."

# Wait for both services to exit
wait

echo "Sustainability Intelligence Platform startup completed."