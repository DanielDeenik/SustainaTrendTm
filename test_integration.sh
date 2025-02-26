#!/bin/bash
set -e

echo "Testing PostgreSQL/FastAPI/Flask integration..."

# Test FastAPI health endpoint
echo "1. Testing FastAPI health endpoint..."
curl -s http://localhost:8000/health
echo ""

# Test FastAPI metrics endpoint
echo "2. Testing FastAPI metrics endpoint..."
curl -s http://localhost:8000/api/metrics | head -30
echo ""

# Test Flask frontend
echo "3. Testing Flask frontend..."
curl -s http://localhost:5001 > /dev/null
if [ $? -eq 0 ]; then
    echo "Flask frontend is accessible"
else
    echo "Error: Flask frontend is not accessible"
fi

# Test Flask dashboard
echo "4. Testing Flask dashboard..."
curl -s http://localhost:5001/dashboard > /dev/null
if [ $? -eq 0 ]; then
    echo "Flask dashboard is accessible"
else
    echo "Error: Flask dashboard is not accessible"
fi

echo "Integration test complete"
