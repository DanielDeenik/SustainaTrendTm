#!/bin/bash

# Exit on error
set -e

echo "🚀 Starting SustainaTrend deployment..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3 first."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed. Please install pip3 first."
    exit 1
fi

# Create and activate virtual environment
echo "📦 Setting up virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
pip3 install -r requirements.txt

# Install Gunicorn if not already installed
if ! pip3 show gunicorn &> /dev/null; then
    echo "📦 Installing Gunicorn..."
    pip3 install gunicorn
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p uploads
mkdir -p vector_db
mkdir -p logs

# Check if .env file exists, if not create from example
if [ ! -f .env ]; then
    echo "⚙️ Creating .env file from example..."
    cp .env.example .env
    echo "⚠️ Please update the .env file with your actual configuration values."
fi

# Set up MongoDB (if not already running)
echo "🗄️ Checking MongoDB..."
if ! command -v mongod &> /dev/null; then
    echo "⚠️ MongoDB is not installed. Please install MongoDB first."
    exit 1
fi

# Start MongoDB if not running
if ! pgrep -x "mongod" > /dev/null; then
    echo "🔄 Starting MongoDB..."
    mongod --fork --logpath /var/log/mongodb.log
fi

# Initialize the vector database
echo "🔍 Initializing vector database..."
python3 src/frontend/run_initialize_pinecone.py

# Set up logging
echo "📝 Setting up logging..."
touch app.log
chmod 666 app.log

# Start the application with Gunicorn
echo "🌐 Starting the application..."
gunicorn --config src/frontend/gunicorn.conf.py src.frontend.app:app

echo "✅ Deployment completed successfully!"
echo "📊 The application is now running at http://localhost:8000"
echo "📝 Logs are available in app.log" 