"""
Test configuration for Sustainability Intelligence Platform.
Contains fixtures and setup for testing the application components.
"""
import os
import sys
import pytest
from datetime import datetime, timedelta
import requests
from unittest.mock import MagicMock

# Add project directories to Python path for importing modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../frontend')))

# Skip tests that require external services 
# if explicitly disabled using environment variable
skip_integration = pytest.mark.skipif(
    os.getenv('SKIP_INTEGRATION_TESTS') == 'true',
    reason="Integration tests disabled via environment variable"
)

# Skip tests that require database connectivity if credentials aren't available
skip_db_tests = pytest.mark.skipif(
    not (os.getenv('DATABASE_URL') or 
        (os.getenv('PGDATABASE') and os.getenv('PGUSER') and 
         os.getenv('PGPASSWORD') and os.getenv('PGHOST'))),
    reason="Missing required database environment variables"
)

# Sample metrics data for testing
@pytest.fixture
def sample_metrics_data():
    """Generate sample metrics data for testing"""
    # Generate dates for the past 3 months
    dates = []
    for i in range(3):
        dates.append((datetime.now() - timedelta(days=30 * (2 - i))).isoformat())

    # Carbon emissions data
    emissions_data = [
        {"id": 1, "name": "Carbon Emissions", "category": "emissions", "value": 45, "unit": "tons CO2e", "timestamp": dates[0]},
        {"id": 2, "name": "Carbon Emissions", "category": "emissions", "value": 42, "unit": "tons CO2e", "timestamp": dates[1]},
        {"id": 3, "name": "Carbon Emissions", "category": "emissions", "value": 38, "unit": "tons CO2e", "timestamp": dates[2]},
    ]

    # Energy consumption data
    energy_data = [
        {"id": 4, "name": "Energy Consumption", "category": "energy", "value": 1250, "unit": "MWh", "timestamp": dates[0]},
        {"id": 5, "name": "Energy Consumption", "category": "energy", "value": 1200, "unit": "MWh", "timestamp": dates[1]},
        {"id": 6, "name": "Energy Consumption", "category": "energy", "value": 1150, "unit": "MWh", "timestamp": dates[2]},
    ]

    # Water usage data
    water_data = [
        {"id": 7, "name": "Water Usage", "category": "water", "value": 350, "unit": "kiloliters", "timestamp": dates[0]},
        {"id": 8, "name": "Water Usage", "category": "water", "value": 340, "unit": "kiloliters", "timestamp": dates[1]},
        {"id": 9, "name": "Water Usage", "category": "water", "value": 330, "unit": "kiloliters", "timestamp": dates[2]},
    ]

    # Waste recycled data
    waste_data = [
        {"id": 10, "name": "Waste Recycled", "category": "waste", "value": 75, "unit": "percent", "timestamp": dates[0]},
        {"id": 11, "name": "Waste Recycled", "category": "waste", "value": 78, "unit": "percent", "timestamp": dates[1]},
        {"id": 12, "name": "Waste Recycled", "category": "waste", "value": 80, "unit": "percent", "timestamp": dates[2]},
    ]

    # ESG score data
    esg_data = [
        {"id": 13, "name": "ESG Score", "category": "social", "value": 78, "unit": "score", "timestamp": dates[0]},
        {"id": 14, "name": "ESG Score", "category": "social", "value": 80, "unit": "score", "timestamp": dates[1]},
        {"id": 15, "name": "ESG Score", "category": "social", "value": 82, "unit": "score", "timestamp": dates[2]},
    ]

    # Combine all data
    all_data = emissions_data + energy_data + water_data + waste_data + esg_data

    return all_data

@pytest.fixture
def mock_response():
    """Create a mock HTTP response for testing"""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.raise_for_status.return_value = None
    return mock_resp

@pytest.fixture
def service_urls():
    """Service URLs for integration testing"""
    return {
        "fastapi": os.getenv("BACKEND_URL", "http://localhost:8000"),
        "flask": os.getenv("FRONTEND_URL", "http://localhost:5001")
    }

# Check if services are running (for integration tests)
def is_service_running(url, timeout=0.5):
    """Check if a service is running at the given URL"""
    try:
        requests.get(f"{url}", timeout=timeout)
        return True
    except requests.exceptions.RequestException:
        return False