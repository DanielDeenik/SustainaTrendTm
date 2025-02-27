"""
Integration tests for the Sustainability Intelligence Platform.
Tests the entire system: PostgreSQL + FastAPI + Flask.
"""
import os
import pytest
import requests
import psycopg2
import time
import socket
from datetime import datetime
from contextlib import closing

# Skip if database environment variables aren't set
pytestmark = pytest.mark.skipif(
    not (os.getenv('DATABASE_URL') or 
        (os.getenv('PGDATABASE') and os.getenv('PGUSER') and 
         os.getenv('PGPASSWORD') and os.getenv('PGHOST'))),
    reason="Missing required database environment variables"
)

# Configuration
FASTAPI_URL = "http://localhost:8000"
FLASK_URL = "http://localhost:5001"
MAX_RETRIES = 5
RETRY_DELAY = 2

def is_port_in_use(port):
    """Check if a port is in use"""
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        return s.connect_ex(('localhost', port)) == 0

def wait_for_service(url, max_retries=MAX_RETRIES):
    """Wait for a service to be available"""
    for i in range(max_retries):
        try:
            response = requests.get(url, timeout=2)
            if response.status_code == 200:
                return True
        except requests.RequestException:
            pass
            
        time.sleep(RETRY_DELAY)
    
    return False

class TestIntegration:
    """Integration tests for the entire system"""
    
    @classmethod
    def setup_class(cls):
        """Setup for all integration tests"""
        # Check that services are running
        cls.fastapi_running = is_port_in_use(8000)
        cls.flask_running = is_port_in_use(5001)
        
        if not cls.fastapi_running:
            pytest.skip("FastAPI service is not running on port 8000")
            
        if not cls.flask_running:
            pytest.skip("Flask service is not running on port 5001")
            
        # Wait for services to be ready
        cls.fastapi_ready = wait_for_service(f"{FASTAPI_URL}/health")
        cls.flask_ready = wait_for_service(FLASK_URL)
        
        if not cls.fastapi_ready:
            pytest.skip("FastAPI service is not responding on /health")
            
        if not cls.flask_ready:
            pytest.skip("Flask service is not responding")
    
    def test_database_connection(self):
        """Test direct connection to PostgreSQL database"""
        # Connect to database
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
        
        # Execute a simple query
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM metrics")
            result = cur.fetchone()
            metric_count = result[0]
        
        conn.close()
        
        # Verify metrics exist
        assert metric_count > 0, "No metrics found in database"
        
    def test_fastapi_health(self):
        """Test FastAPI health endpoint"""
        response = requests.get(f"{FASTAPI_URL}/health", timeout=5)
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert data["database"] == "connected"
        assert "timestamp" in data
    
    def test_fastapi_metrics(self):
        """Test FastAPI metrics endpoint"""
        response = requests.get(f"{FASTAPI_URL}/api/metrics", timeout=5)
        assert response.status_code == 200
        
        metrics = response.json()
        assert len(metrics) > 0
        
        # Verify metrics structure
        sample_metric = metrics[0]
        assert "id" in sample_metric
        assert "name" in sample_metric
        assert "category" in sample_metric
        assert "value" in sample_metric
        assert "unit" in sample_metric
        assert "timestamp" in sample_metric
    
    def test_flask_home(self):
        """Test Flask home page"""
        response = requests.get(FLASK_URL, timeout=5)
        assert response.status_code == 200
        
        # Home page should contain expected text
        assert "Sustainability" in response.text
    
    def test_flask_dashboard(self):
        """Test Flask dashboard page"""
        response = requests.get(f"{FLASK_URL}/dashboard", timeout=5)
        assert response.status_code == 200
        
        # Dashboard should contain metrics
        assert "Carbon Emissions" in response.text
        assert "Energy Consumption" in response.text
        assert "Water Usage" in response.text
        assert "Waste Recycled" in response.text
        assert "ESG Score" in response.text
    
    def test_flask_api_metrics(self):
        """Test Flask API metrics endpoint"""
        response = requests.get(f"{FLASK_URL}/api/metrics", timeout=5)
        assert response.status_code == 200
        
        metrics = response.json()
        assert len(metrics) > 0
        
        # Verify metrics structure matches
        sample_metric = metrics[0]
        assert "id" in sample_metric
        assert "name" in sample_metric
        assert "category" in sample_metric
        assert "value" in sample_metric
        assert "unit" in sample_metric
        assert "timestamp" in sample_metric
    
    def test_data_consistency(self):
        """Test data consistency between FastAPI and Flask"""
        # Get metrics from FastAPI
        fastapi_response = requests.get(f"{FASTAPI_URL}/api/metrics", timeout=5)
        fastapi_metrics = fastapi_response.json()
        
        # Get metrics from Flask
        flask_response = requests.get(f"{FLASK_URL}/api/metrics", timeout=5)
        flask_metrics = flask_response.json()
        
        # Either both should have the same data directly from PostgreSQL
        # or Flask metrics should be mock data if FastAPI is down
        
        # If FastAPI has data, it should match Flask data
        if len(fastapi_metrics) > 0:
            # Compare metrics count (they might not be exactly equal if caching or mock data is used)
            assert len(flask_metrics) > 0
            
            # Compare metric structure
            assert set(fastapi_metrics[0].keys()) == set(flask_metrics[0].keys())
            
            # Compare metric categories - testing that the same categories exist in both
            fastapi_categories = set(m["category"] for m in fastapi_metrics)
            flask_categories = set(m["category"] for m in flask_metrics)
            
            # Flask should have at least the same categories as FastAPI
            assert fastapi_categories.issubset(flask_categories)
