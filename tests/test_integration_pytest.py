"""
Integration tests for the PostgreSQL/FastAPI/Flask system.
Uses pytest to ensure all components work together.
"""
import os
import pytest
import requests
import psycopg2
import time
import subprocess
import signal
from datetime import datetime

# Verify database connection parameters are available
pytestmark = pytest.mark.skipif(
    not (os.getenv('DATABASE_URL') or 
        (os.getenv('PGDATABASE') and os.getenv('PGUSER') and 
         os.getenv('PGPASSWORD') and os.getenv('PGHOST'))),
    reason="Missing required database environment variables"
)

@pytest.fixture(scope="module")
def db_connection():
    """Create a database connection for testing"""
    if os.getenv('DATABASE_URL'):
        conn = psycopg2.connect(os.getenv('DATABASE_URL'))
    else:
        conn = psycopg2.connect(
            dbname=os.getenv('PGDATABASE'),
            user=os.getenv('PGUSER'),
            password=os.getenv('PGPASSWORD'),
            host=os.getenv('PGHOST'),
            port=os.getenv('PGPORT', '5432')
        )
    
    yield conn
    conn.close()

def test_database_connection(db_connection):
    """Test direct connection to PostgreSQL database"""
    with db_connection.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM metrics")
        result = cur.fetchone()
        assert result is not None
        metric_count = result[0]
        assert metric_count > 0, "No metrics found in database"

def test_fastapi_health():
    """Test FastAPI health endpoint"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        assert response.status_code == 200
        health_data = response.json()
        assert health_data["status"] == "healthy"
        assert "database" in health_data
        assert "timestamp" in health_data
    except requests.exceptions.ConnectionError:
        pytest.skip("FastAPI service not running on port 8000")

def test_fastapi_metrics():
    """Test FastAPI metrics endpoint"""
    try:
        response = requests.get("http://localhost:8000/api/metrics", timeout=5)
        assert response.status_code == 200
        metrics = response.json()
        assert isinstance(metrics, list)
        assert len(metrics) > 0
        
        # Verify first metric has expected structure
        first_metric = metrics[0]
        assert "id" in first_metric
        assert "name" in first_metric
        assert "category" in first_metric
        assert "value" in first_metric
        assert "unit" in first_metric
        assert "timestamp" in first_metric
    except requests.exceptions.ConnectionError:
        pytest.skip("FastAPI service not running on port 8000")

def test_flask_frontend():
    """Test Flask frontend is accessible"""
    try:
        response = requests.get("http://localhost:5001", timeout=5)
        assert response.status_code == 200
    except requests.exceptions.ConnectionError:
        pytest.skip("Flask service not running on port 5001")

def test_flask_dashboard():
    """Test Flask dashboard is loading metrics data"""
    try:
        response = requests.get("http://localhost:5001/dashboard", timeout=5)
        assert response.status_code == 200
        
        # Check for key dashboard elements
        html_content = response.text
        assert "Sustainability Intelligence Dashboard" in html_content or "Sustainability Metrics" in html_content
        assert "Carbon Emissions" in html_content
    except requests.exceptions.ConnectionError:
        pytest.skip("Flask service not running on port 5001")

def test_flask_api_metrics():
    """Test that Flask can access metrics data (either mock or from FastAPI)"""
    try:
        response = requests.get("http://localhost:5001/api/metrics", timeout=5)
        assert response.status_code == 200
        
        metrics = response.json()
        assert isinstance(metrics, list)
        assert len(metrics) > 0
        
        # Verify metrics structure
        assert "name" in metrics[0]
        assert "category" in metrics[0]
        assert "value" in metrics[0]
    except requests.exceptions.ConnectionError:
        pytest.skip("Flask service not running on port 5001")

# This test will be added later when we implement trend analysis
@pytest.mark.skip(reason="Trend analysis feature not implemented yet")
def test_trend_analysis_integration():
    """Test that the trend analysis dashboard integrates with the metrics data"""
    try:
        response = requests.get("http://localhost:5001/trend-analysis", timeout=5)
        assert response.status_code == 200
        assert "Sustainability Trend Analysis" in response.text
        
        # Check that metrics data is being used in the trend analysis
        assert "Carbon Emissions" in response.text
        assert "virality_score" in response.text.lower()
    except requests.exceptions.ConnectionError:
        pytest.skip("Flask service not running on port 5001")
