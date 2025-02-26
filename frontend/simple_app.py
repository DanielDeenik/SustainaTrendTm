from flask import Flask, render_template, jsonify
import requests
import os
import logging
from datetime import datetime, timedelta
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask
app = Flask(__name__)

# FastAPI backend URL - use port 8000
BACKEND_URL = os.getenv('BACKEND_URL', 'http://localhost:8000')

def get_sustainability_metrics():
    """Fetch sustainability metrics from FastAPI backend"""
    try:
        logger.info(f"Fetching metrics from FastAPI backend: {BACKEND_URL}/api/metrics")
        response = requests.get(f"{BACKEND_URL}/api/metrics", timeout=10.0)
        response.raise_for_status()

        metrics_data = response.json()
        logger.info(f"Successfully fetched {len(metrics_data)} metrics from API")

        # Log a sample metric for verification
        if metrics_data and len(metrics_data) > 0:
            logger.info(f"Sample metric: {json.dumps(metrics_data[0], indent=2)}")
        
        return metrics_data
    except Exception as e:
        logger.error(f"Error fetching metrics from API: {str(e)}")
        logger.info("Falling back to mock data")
        return get_mock_sustainability_metrics()

# Fallback mock data function
def get_mock_sustainability_metrics():
    """Generate mock sustainability metrics data as fallback"""
    logger.info("Generating mock sustainability metrics data")
    # Generate dates for the past 6 months
    dates = []
    for i in range(6):
        dates.append((datetime.now() - timedelta(days=30 * (5 - i))).isoformat())

    # Carbon emissions data (decreasing trend - good)
    emissions_data = [
        {"id": 1, "name": "Carbon Emissions", "category": "emissions", "value": 45, "unit": "tons CO2e", "timestamp": dates[0]},
        {"id": 2, "name": "Carbon Emissions", "category": "emissions", "value": 42, "unit": "tons CO2e", "timestamp": dates[1]},
        {"id": 3, "name": "Carbon Emissions", "category": "emissions", "value": 38, "unit": "tons CO2e", "timestamp": dates[2]},
        {"id": 4, "name": "Carbon Emissions", "category": "emissions", "value": 35, "unit": "tons CO2e", "timestamp": dates[3]},
        {"id": 5, "name": "Carbon Emissions", "category": "emissions", "value": 32, "unit": "tons CO2e", "timestamp": dates[4]},
        {"id": 6, "name": "Carbon Emissions", "category": "emissions", "value": 30, "unit": "tons CO2e", "timestamp": dates[5]}
    ]

    # Energy consumption data (decreasing trend - good)
    energy_data = [
        {"id": 7, "name": "Energy Consumption", "category": "energy", "value": 1250, "unit": "MWh", "timestamp": dates[0]},
        {"id": 8, "name": "Energy Consumption", "category": "energy", "value": 1200, "unit": "MWh", "timestamp": dates[1]},
        {"id": 9, "name": "Energy Consumption", "category": "energy", "value": 1150, "unit": "MWh", "timestamp": dates[2]},
        {"id": 10, "name": "Energy Consumption", "category": "energy", "value": 1100, "unit": "MWh", "timestamp": dates[3]},
        {"id": 11, "name": "Energy Consumption", "category": "energy", "value": 1075, "unit": "MWh", "timestamp": dates[4]},
        {"id": 12, "name": "Energy Consumption", "category": "energy", "value": 1050, "unit": "MWh", "timestamp": dates[5]}
    ]

    # Water usage data (decreasing trend - good)
    water_data = [
        {"id": 13, "name": "Water Usage", "category": "water", "value": 350, "unit": "kiloliters", "timestamp": dates[0]},
        {"id": 14, "name": "Water Usage", "category": "water", "value": 340, "unit": "kiloliters", "timestamp": dates[1]},
        {"id": 15, "name": "Water Usage", "category": "water", "value": 330, "unit": "kiloliters", "timestamp": dates[2]},
        {"id": 16, "name": "Water Usage", "category": "water", "value": 320, "unit": "kiloliters", "timestamp": dates[3]},
        {"id": 17, "name": "Water Usage", "category": "water", "value": 310, "unit": "kiloliters", "timestamp": dates[4]},
        {"id": 18, "name": "Water Usage", "category": "water", "value": 300, "unit": "kiloliters", "timestamp": dates[5]}
    ]

    # Waste reduction data (increasing trend - good)
    waste_data = [
        {"id": 19, "name": "Waste Recycled", "category": "waste", "value": 65, "unit": "percent", "timestamp": dates[0]},
        {"id": 20, "name": "Waste Recycled", "category": "waste", "value": 68, "unit": "percent", "timestamp": dates[1]},
        {"id": 21, "name": "Waste Recycled", "category": "waste", "value": 72, "unit": "percent", "timestamp": dates[2]},
        {"id": 22, "name": "Waste Recycled", "category": "waste", "value": 76, "unit": "percent", "timestamp": dates[3]},
        {"id": 23, "name": "Waste Recycled", "category": "waste", "value": 80, "unit": "percent", "timestamp": dates[4]},
        {"id": 24, "name": "Waste Recycled", "category": "waste", "value": 82, "unit": "percent", "timestamp": dates[5]}
    ]

    # ESG score data (increasing trend - good)
    esg_data = [
        {"id": 25, "name": "ESG Score", "category": "social", "value": 72, "unit": "score", "timestamp": dates[0]},
        {"id": 26, "name": "ESG Score", "category": "social", "value": 74, "unit": "score", "timestamp": dates[1]},
        {"id": 27, "name": "ESG Score", "category": "social", "value": 76, "unit": "score", "timestamp": dates[2]},
        {"id": 28, "name": "ESG Score", "category": "social", "value": 78, "unit": "score", "timestamp": dates[3]},
        {"id": 29, "name": "ESG Score", "category": "social", "value": 80, "unit": "score", "timestamp": dates[4]},
        {"id": 30, "name": "ESG Score", "category": "social", "value": 82, "unit": "score", "timestamp": dates[5]}
    ]

    # Combine all data
    all_data = emissions_data + energy_data + water_data + waste_data + esg_data

    logger.info(f"Generated mock sustainability metrics with {len(all_data)} records")
    return all_data

# Routes
@app.route('/')
def home():
    """Home page"""
    return render_template("index.html")

@app.route('/dashboard')
def dashboard():
    """Dashboard page using data from FastAPI backend"""
    logger.info("Dashboard page requested, fetching metrics...")
    metrics = get_sustainability_metrics()
    logger.info(f"Rendering dashboard with {len(metrics)} metrics")
    return render_template("dashboard.html", metrics=metrics)

@app.route('/api/metrics')
def api_metrics():
    """API endpoint for metrics data"""
    logger.info("API metrics endpoint called")
    metrics = get_sustainability_metrics()
    logger.info(f"Returning {len(metrics)} metrics from API endpoint")
    return jsonify(metrics)

@app.route('/debug')
def debug_route():
    """Debug route to check registered routes and connections"""
    logger.info("Debug route called")
    routes = [str(rule) for rule in app.url_map.iter_rules()]

    # Also check FastAPI connection
    try:
        logger.info(f"Testing connection to FastAPI backend: {BACKEND_URL}/health")
        response = requests.get(f"{BACKEND_URL}/health", timeout=5.0)
        response.raise_for_status()
        backend_status = response.json()
        logger.info(f"FastAPI backend health check: {backend_status}")
    except Exception as e:
        logger.error(f"Failed to connect to FastAPI backend: {str(e)}")
        backend_status = {"status": "error", "message": str(e)}

    debug_info = {
        "routes": routes,
        "backend_url": BACKEND_URL,
        "backend_status": backend_status
    }

    return jsonify(debug_info)

if __name__ == "__main__":
    # Use port 5001 to avoid conflicts
    port = 5001
    logger.info(f"Starting Flask frontend on port {port}")
    app.run(host="0.0.0.0", port=port, debug=True)
