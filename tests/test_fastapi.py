"""
Unit tests for the FastAPI backend endpoints.
"""
import os
import pytest
import json
from datetime import datetime
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

# Skip if database environment variables aren't set
pytestmark = pytest.mark.skipif(
    not (os.getenv('DATABASE_URL') or 
        (os.getenv('PGDATABASE') and os.getenv('PGUSER') and 
         os.getenv('PGPASSWORD') and os.getenv('PGHOST'))),
    reason="Missing required database environment variables"
)

# Import the FastAPI app after the environment check
from backend.simple_api import app

@pytest.fixture
def api_client():
    """Create a FastAPI test client"""
    return TestClient(app)

@pytest.fixture
def mock_db_connection():
    """Mock database connection for testing"""
    # Create a mock connection and cursor
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    
    # Mock context manager for cursor
    mock_conn.__enter__.return_value = mock_conn
    mock_conn.__exit__.return_value = None
    
    # Return the mock objects for use in tests
    return mock_conn, mock_cursor

def test_health_endpoint(api_client):
    """Test the health check endpoint"""
    response = api_client.get("/health")
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "healthy" or data["status"] == "unhealthy"
    assert "database" in data
    assert "timestamp" in data

@patch("backend.simple_api.get_db_connection")
def test_metrics_endpoint_success(mock_get_conn, api_client, sample_metrics_data, mock_db_connection):
    """Test the metrics endpoint with successful response"""
    mock_conn, mock_cursor = mock_db_connection
    mock_get_conn.return_value = mock_conn
    
    # Mock the database response
    mock_cursor.fetchall.return_value = [
        {
            'id': m['id'], 
            'name': m['name'], 
            'category': m['category'], 
            'value': m['value'], 
            'unit': m['unit'],
            'timestamp': datetime.fromisoformat(m['timestamp'])
        }
        for m in sample_metrics_data
    ]
    
    # Test the endpoint
    response = api_client.get("/api/metrics")
    assert response.status_code == 200
    
    # Verify the response data
    data = response.json()
    assert len(data) == len(sample_metrics_data)
    
    # Check first item
    assert data[0]['name'] == sample_metrics_data[0]['name']
    assert data[0]['category'] == sample_metrics_data[0]['category']
    assert data[0]['value'] == float(sample_metrics_data[0]['value'])
    assert data[0]['unit'] == sample_metrics_data[0]['unit']

@patch("backend.simple_api.get_db_connection")
def test_metrics_endpoint_db_error(mock_get_conn, api_client):
    """Test metrics endpoint with database error"""
    # Simulate a database error
    mock_get_conn.side_effect = Exception("Database connection failed")
    
    # Test the endpoint with error
    response = api_client.get("/api/metrics")
    assert response.status_code == 500
    
    # Verify error message
    data = response.json()
    assert "detail" in data
    assert "Failed to fetch metrics" in data["detail"]
