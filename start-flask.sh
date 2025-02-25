#!/bin/bash
set -e

# Install Python dependencies
pip install --quiet flask flask-sqlalchemy psycopg2-binary python-dotenv

# Set environment variables
export FLASK_APP=app.py
export FLASK_ENV=development
export FLASK_DEBUG=1

# Give execute permission to app.py
chmod +x app.py

# Start Flask server with proper output handling
echo "Starting Flask server on port 5000..."
exec python app.py 2>&1