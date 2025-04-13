# SustainaTrend Deployment Script for Windows
Write-Host "Starting SustainaTrend deployment..." -ForegroundColor Green

# Check if Python is installed
try {
    $pythonVersion = python --version
    Write-Host "Python is installed: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "Python is not installed. Please install Python 3 first." -ForegroundColor Red
    exit 1
}

# Check if pip is installed
try {
    $pipVersion = pip --version
    Write-Host "pip is installed: $pipVersion" -ForegroundColor Green
} catch {
    Write-Host "pip is not installed. Please install pip first." -ForegroundColor Red
    exit 1
}

# Create and activate virtual environment
Write-Host "Setting up virtual environment..." -ForegroundColor Yellow
if (-not (Test-Path "venv")) {
    python -m venv venv
}
.\venv\Scripts\Activate.ps1

# Install dependencies
Write-Host "Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

# Install waitress for Windows deployment
Write-Host "Installing waitress..." -ForegroundColor Yellow
pip install waitress

# Create necessary directories
Write-Host "Creating necessary directories..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path "uploads"
New-Item -ItemType Directory -Force -Path "vector_db"
New-Item -ItemType Directory -Force -Path "logs"

# Check if .env file exists, if not create from example
if (-not (Test-Path ".env")) {
    Write-Host "Creating .env file from example..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "Please update the .env file with your actual configuration values." -ForegroundColor Red
}

# Set up MongoDB (if not already running)
Write-Host "Checking MongoDB..." -ForegroundColor Yellow
try {
    $mongodbVersion = mongod --version
    Write-Host "MongoDB is installed: $mongodbVersion" -ForegroundColor Green
} catch {
    Write-Host "MongoDB is not installed. Please install MongoDB first." -ForegroundColor Red
    Write-Host "Download MongoDB from: https://www.mongodb.com/try/download/community" -ForegroundColor Yellow
    exit 1
}

# Start MongoDB if not running
$mongodbProcess = Get-Process mongod -ErrorAction SilentlyContinue
if (-not $mongodbProcess) {
    Write-Host "Starting MongoDB..." -ForegroundColor Yellow
    Start-Process mongod -ArgumentList "--dbpath", "data/db"
}

# Initialize the vector database
Write-Host "Initializing vector database..." -ForegroundColor Yellow
python src/frontend/run_initialize_pinecone.py

# Set up logging
Write-Host "Setting up logging..." -ForegroundColor Yellow
if (-not (Test-Path "app.log")) {
    New-Item -ItemType File -Force -Path "app.log"
}

# Start the application with waitress
Write-Host "Starting the application..." -ForegroundColor Green
$env:FLASK_APP = "src/frontend/app.py"
$env:FLASK_ENV = "production"

# Create a startup script
$startupScript = @"
from waitress import serve
from src.frontend.app import app

if __name__ == '__main__':
    serve(app, host='0.0.0.0', port=8000)
"@

Set-Content -Path "start_server.py" -Value $startupScript

# Start the server
Write-Host "Starting the server..." -ForegroundColor Green
Start-Process python -ArgumentList "start_server.py" -NoNewWindow

Write-Host "Deployment completed successfully!" -ForegroundColor Green
Write-Host "The application is now running at http://localhost:8000" -ForegroundColor Cyan
Write-Host "Logs are available in app.log" -ForegroundColor Cyan 