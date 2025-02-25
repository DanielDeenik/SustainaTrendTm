#!/bin/bash
set -e

# Install Python dependencies
pip install --quiet flask flask-sqlalchemy psycopg2-binary python-dotenv

# Set environment variables
export FLASK_APP=app.py
export FLASK_ENV=development
export FLASK_DEBUG=1

# Start Flask server
echo "Starting Flask server on port 5000..."
exec python -m flask run --host=0.0.0.0 --port=5000