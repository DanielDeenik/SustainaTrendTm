"""
Unit tests for the Flask frontend.
"""
import os
import pytest
from unittest.mock import patch, MagicMock
import json
from flask.testing import FlaskClient

# Import the Flask app
from frontend.simple_app import app

@pytest.fixture
def flask_client():
    """Create a Flask test client"""
    app.config['TESTING'] = True

    # Disable caching for testing
    app.config['CACHE_TYPE'] = 'null'

    with app.test_client() as client:
        yield client

@pytest.fixture
def mock_response():
    """Create a mock successful response from requests"""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.raise_for_status.return_value = None
    return mock_resp

@pytest.fixture
def sample_metrics_data():
    """Sample metrics data for testing"""
    return [
        {"id": 1, "name": "Carbon Emissions", "category": "emissions", "value": 45.0, "unit": "tons CO2e", "timestamp": "2023-01-01T00:00:00"},
        {"id": 2, "name": "Energy Consumption", "category": "energy", "value": 1250.0, "unit": "MWh", "timestamp": "2023-01-01T00:00:00"},
        {"id": 3, "name": "Water Usage", "category": "water", "value": 350.0, "unit": "kiloliters", "timestamp": "2023-02-01T00:00:00"},
        {"id": 4, "name": "Waste Recycled", "category": "waste", "value": 75.0, "unit": "percent", "timestamp": "2023-03-01T00:00:00"},
        {"id": 5, "name": "ESG Score", "category": "social", "value": 80.0, "unit": "score", "timestamp": "2023-03-01T00:00:00"}
    ]

@patch('frontend.simple_app.requests.get')
def test_home_route(mock_get, flask_client):
    """Test the home route"""
    # Make a request to the home route
    response = flask_client.get('/')

    # Should return 200 OK
    assert response.status_code == 200

    # Verify request to backend was not made for home route
    mock_get.assert_not_called()

@patch('frontend.simple_app.requests.get')
def test_dashboard_route(mock_get, flask_client, sample_metrics_data, mock_response):
    """Test the dashboard route"""
    # Configure mock to return sample metrics data
    mock_response.json.return_value = sample_metrics_data
    mock_get.return_value = mock_response

    # Make a request to the dashboard route
    response = flask_client.get('/dashboard')

    # Should return 200 OK
    assert response.status_code == 200

    # Verify request to backend was made
    mock_get.assert_called_once()

    # Dashboard should contain metric names
    response_data = response.data.decode('utf-8')
    assert "Carbon Emissions" in response_data
    assert "Energy Consumption" in response_data

@patch('frontend.simple_app.requests.get')
def test_api_metrics_route(mock_get, flask_client, sample_metrics_data, mock_response):
    """Test the API metrics route"""
    # Configure mock to return sample metrics data
    mock_response.json.return_value = sample_metrics_data
    mock_get.return_value = mock_response

    # Make a request to the API metrics route
    response = flask_client.get('/api/metrics')

    # Should return 200 OK
    assert response.status_code == 200

    # Verify request to backend was made
    mock_get.assert_called_once()

    # Verify response contains the metrics data
    response_data = json.loads(response.data)
    assert len(response_data) == len(sample_metrics_data)
    assert response_data[0]['name'] == sample_metrics_data[0]['name']
    assert response_data[0]['category'] == sample_metrics_data[0]['category']

@patch('frontend.simple_app.requests.get')
def test_api_metrics_route_backend_failure(mock_get, flask_client, mock_response):
    """Test the API metrics route with backend failure"""
    # Configure mock to simulate FastAPI backend failure
    mock_get.side_effect = Exception("Connection failed")

    # Make a request to the API metrics route
    response = flask_client.get('/api/metrics')

    # Should still return 200 OK (because it falls back to mock data)
    assert response.status_code == 200

    # Response data should still be valid JSON
    response_data = json.loads(response.data)
    assert len(response_data) > 0
    assert 'name' in response_data[0]
    assert 'category' in response_data[0]

@patch('frontend.simple_app.requests.get')
def test_debug_route(mock_get, flask_client, mock_response):
    """Test the debug route"""
    # Configure mock to return health check data
    mock_response.json.return_value = {
        "status": "healthy",
        "database": "connected",
        "timestamp": "2023-01-01T00:00:00"
    }
    mock_get.return_value = mock_response

    # Make a request to the debug route
    response = flask_client.get('/debug')

    # Should return 200 OK
    assert response.status_code == 200

    # Verify health check request to backend was made
    mock_get.assert_called_once()
    assert '/health' in mock_get.call_args[0][0]

    # Verify response contains debug info
    response_data = json.loads(response.data)
    assert 'routes' in response_data
    assert 'backend_url' in response_data
    assert 'backend_status' in response_data

# Add tests for the new sustainability trend analysis features
def test_trend_analysis_route_exists(flask_client):
    """Test that the trend analysis route exists"""
    # This test will fail initially until we implement the route
    response = flask_client.get('/trend-analysis')
    assert response.status_code == 200
    assert "Sustainability Trend Analysis" in response.data.decode('utf-8')