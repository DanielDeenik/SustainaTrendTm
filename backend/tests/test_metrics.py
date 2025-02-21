import pytest
from fastapi.testclient import TestClient
from datetime import datetime
from backend.main import app

client = TestClient(app)

def test_get_metrics():
    response = client.get("/api/metrics")
    assert response.status_code == 200
    metrics = response.json()
    assert isinstance(metrics, list)
    if len(metrics) > 0:
        metric = metrics[0]
        assert "id" in metric
        assert "name" in metric
        assert "category" in metric
        assert "value" in metric
        assert "unit" in metric
        assert "timestamp" in metric
        assert "metric_metadata" in metric

def test_get_metrics_by_category():
    response = client.get("/api/metrics?category=emissions")
    assert response.status_code == 200
    metrics = response.json()
    assert isinstance(metrics, list)
    for metric in metrics:
        assert metric["category"] == "emissions"

def test_create_metric():
    test_metric = {
        "name": "Test Metric",
        "category": "emissions",
        "value": 123.45,
        "unit": "kg CO2e",
        "metric_metadata": {
            "source": "test",
            "location": "test facility"
        }
    }
    response = client.post("/api/metrics", json=test_metric)
    assert response.status_code == 201
    created_metric = response.json()
    assert created_metric["name"] == test_metric["name"]
    assert created_metric["category"] == test_metric["category"]
    assert created_metric["value"] == test_metric["value"]
    assert created_metric["unit"] == test_metric["unit"]
    assert created_metric["metric_metadata"] == test_metric["metric_metadata"]
    assert "id" in created_metric
    assert "timestamp" in created_metric

def test_create_metric_invalid_category():
    test_metric = {
        "name": "Invalid Category Metric",
        "category": "invalid_category",
        "value": 100,
        "unit": "kg",
        "metric_metadata": {}
    }
    response = client.post("/api/metrics", json=test_metric)
    assert response.status_code == 422

def test_create_metric_invalid_value():
    test_metric = {
        "name": "Invalid Value Metric",
        "category": "emissions",
        "value": -100,  # Negative value should be rejected
        "unit": "kg",
        "metric_metadata": {}
    }
    response = client.post("/api/metrics", json=test_metric)
    assert response.status_code == 422

def test_create_metric_missing_required_fields():
    test_metric = {
        "name": "Missing Fields Metric",
        # Missing category and value
        "unit": "kg"
    }
    response = client.post("/api/metrics", json=test_metric)
    assert response.status_code == 422

def test_create_metric_invalid_json():
    response = client.post(
        "/api/metrics",
        headers={"Content-Type": "application/json"},
        content="invalid json content"
    )
    assert response.status_code == 422

def test_get_metrics_invalid_category():
    response = client.get("/api/metrics?category=nonexistent")
    assert response.status_code == 200
    metrics = response.json()
    assert isinstance(metrics, list)
    assert len(metrics) == 0