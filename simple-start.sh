#!/bin/bash
set -e

echo "Starting Sustainability Intelligence Platform..."

# Create logs directory
mkdir -p logs

# Kill any existing processes
echo "Stopping any existing services..."
pkill -f "python" || true
pkill -f "flask" || true
pkill -f "uvicorn" || true
pkill -f "port 5000" || true
pkill -f "port 5001" || true
pkill -f "port 8000" || true
pkill -f "redis-server" || true

sleep 2  # Give processes time to terminate

# Make scripts executable
chmod +x backend/seed_database.py

# Display database connection info (without sensitive values)
echo "Database configuration:"
echo "- DATABASE_URL exists: $(if [ -n "$DATABASE_URL" ]; then echo "yes"; else echo "no"; fi)"
echo "- PGDATABASE exists: $(if [ -n "$PGDATABASE" ]; then echo "yes"; else echo "no"; fi)"
echo "- PGUSER exists: $(if [ -n "$PGUSER" ]; then echo "yes"; else echo "no"; fi)"
echo "- PGHOST exists: $(if [ -n "$PGHOST" ]; then echo "yes"; else echo "no"; fi)"
echo "- PGPORT exists: $(if [ -n "$PGPORT" ]; then echo "yes"; else echo "no"; fi)"

# Seed the database with sample metrics
echo "Seeding database with sample metrics..."
cd backend
python seed_database.py || echo "Warning: Database seeding failed, but continuing startup"
cd ..

# Start FastAPI backend (using simplified version)
echo "Starting FastAPI backend on port 8000..."
cd backend
python simple_api.py > ../logs/fastapi.log 2>&1 &
FASTAPI_PID=$!
cd ..

# Give FastAPI time to start
echo "Waiting for FastAPI backend to start..."
sleep 5

# Start Flask frontend (using simplified version)
echo "Starting Flask frontend on port 5001..."
cd frontend
# Set the backend URL environment variable
export BACKEND_URL="http://localhost:8000"
python simple_app.py > ../logs/flask.log 2>&1 &
FLASK_PID=$!
cd ..

# Sleep to give services time to start
sleep 5

# Verify FastAPI is running
echo "Checking FastAPI health..."
curl -s http://localhost:8000/health || echo "Warning: FastAPI health check failed"

echo "Services started with PIDs:"
echo "- FastAPI: $FASTAPI_PID"
echo "- Flask: $FLASK_PID"

echo "Access the web interface at: http://localhost:5001"
echo "Access the API at: http://localhost:8000/api/metrics"

echo "Press Ctrl+C to stop all services"

# Wait for both processes
wait $FASTAPI_PID $FLASK_PID
