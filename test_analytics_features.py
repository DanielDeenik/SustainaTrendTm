#!/usr/bin/env python3
"""
Test script for the AI-powered analytics features
of the Sustainability Intelligence Platform
"""
import requests
import json
import time
import sys
import os
from datetime import datetime

# Configuration
FLASK_URL = "http://localhost:5000"
FASTAPI_URL = "http://localhost:8000"
TEST_COMPANY = "GreenTech Solutions"
TEST_INDUSTRY = "Technology"

print("============ Sustainability Intelligence Platform Analytics Test ============")
print(f"Testing Flask Frontend: {FLASK_URL}")
print(f"Testing FastAPI Backend: {FASTAPI_URL}")
print("=" * 75)
print("")

def test_frontend_dashboard():
    """Test if the analytics dashboard page loads correctly"""
    print("Testing Analytics Dashboard Page...")
    try:
        response = requests.get(f"{FLASK_URL}/analytics-dashboard", timeout=10)
        if response.status_code == 200:
            print("✅ Analytics Dashboard page loaded successfully")
            return True
        else:
            print(f"❌ Failed to load Analytics Dashboard: Status code {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing analytics dashboard: {str(e)}")
        return False

def test_predictive_analytics_endpoint(direct=False):
    """Test the predictive analytics endpoint"""
    url = f"{FASTAPI_URL}/api/predictive-analytics" if direct else f"{FLASK_URL}/api/predictive-analytics"
    endpoint_type = "Backend (direct)" if direct else "Frontend (proxy)"
    
    print(f"Testing {endpoint_type} Predictive Analytics Endpoint...")
    
    # Sample data for testing
    data = {
        "company_name": TEST_COMPANY,
        "industry": TEST_INDUSTRY,
        "forecast_periods": 3,
        "metrics": generate_sample_metrics()
    }
    
    try:
        if direct:
            # For direct backend testing, use params for company info
            response = requests.post(
                url, 
                params={
                    "company_name": data["company_name"],
                    "industry": data["industry"],
                    "forecast_periods": data["forecast_periods"]
                },
                json=data["metrics"],
                timeout=30
            )
        else:
            # For frontend proxy, send everything in the body
            response = requests.post(url, json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            validate_predictive_analytics(result)
            return True
        else:
            print(f"❌ Failed to get predictive analytics: Status code {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error testing predictive analytics endpoint: {str(e)}")
        return False

def test_materiality_assessment_endpoint(direct=False):
    """Test the materiality assessment endpoint"""
    url = f"{FASTAPI_URL}/api/materiality-assessment" if direct else f"{FLASK_URL}/api/materiality-assessment"
    endpoint_type = "Backend (direct)" if direct else "Frontend (proxy)"
    
    print(f"Testing {endpoint_type} Materiality Assessment Endpoint...")
    
    # Sample data for testing
    data = {
        "company_name": TEST_COMPANY,
        "industry": TEST_INDUSTRY,
        "metrics": generate_sample_metrics()
    }
    
    try:
        if direct:
            # For direct backend testing, use params for company info
            response = requests.post(
                url, 
                params={
                    "company_name": data["company_name"],
                    "industry": data["industry"]
                },
                json=data["metrics"],
                timeout=30
            )
        else:
            # For frontend proxy, send everything in the body
            response = requests.post(url, json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            validate_materiality_assessment(result)
            return True
        else:
            print(f"❌ Failed to get materiality assessment: Status code {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error testing materiality assessment endpoint: {str(e)}")
        return False

def validate_predictive_analytics(result):
    """Validate the predictive analytics response structure"""
    required_keys = ["company", "industry", "forecast_periods", "predictions", "ai_insights"]
    prediction_keys = ["name", "category", "current_value", "unit", "predicted_values"]
    
    # Check if all required keys are present
    missing_keys = [key for key in required_keys if key not in result]
    if missing_keys:
        print(f"❌ Missing required keys in predictive analytics response: {missing_keys}")
        return False
    
    # Check if predictions array is populated
    if not result["predictions"] or not isinstance(result["predictions"], list):
        print("❌ Predictions array is empty or not an array")
        return False
    
    # Check if predictions have all required fields
    for prediction in result["predictions"]:
        missing_pred_keys = [key for key in prediction_keys if key not in prediction]
        if missing_pred_keys:
            print(f"❌ Missing required keys in prediction: {missing_pred_keys}")
            return False
    
    # Success!
    print(f"✅ Predictive analytics response is valid with {len(result['predictions'])} predictions")
    print(f"✅ AI Insights: {len(result.get('ai_insights', []))} insights provided")
    return True

def validate_materiality_assessment(result):
    """Validate the materiality assessment response structure"""
    required_keys = ["company", "industry", "assessment_date", "material_topics"]
    topic_keys = ["topic", "business_impact_score", "stakeholder_concern_score", "materiality_score"]
    
    # Check if all required keys are present
    missing_keys = [key for key in required_keys if key not in result]
    if missing_keys:
        print(f"❌ Missing required keys in materiality assessment response: {missing_keys}")
        return False
    
    # Check if material_topics array is populated
    if not result["material_topics"] or not isinstance(result["material_topics"], list):
        print("❌ Material topics array is empty or not an array")
        return False
    
    # Check if material topics have all required fields
    for topic in result["material_topics"]:
        missing_topic_keys = [key for key in topic_keys if key not in topic]
        if missing_topic_keys:
            print(f"❌ Missing required keys in material topic: {missing_topic_keys}")
            return False
    
    # Success!
    print(f"✅ Materiality assessment response is valid with {len(result['material_topics'])} material topics")
    # Print the top 3 material topics by score
    top_topics = sorted(result["material_topics"], key=lambda x: x.get("materiality_score", 0), reverse=True)[:3]
    print("Top 3 material topics:")
    for idx, topic in enumerate(top_topics):
        print(f"  {idx+1}. {topic.get('topic')}: {topic.get('materiality_score')}")
    return True

def generate_sample_metrics():
    """Generate sample sustainability metrics data"""
    metrics = []
    categories = ["emissions", "energy", "water", "waste", "social"]
    names = {
        "emissions": "Carbon Emissions",
        "energy": "Energy Consumption",
        "water": "Water Usage",
        "waste": "Waste Recycled",
        "social": "ESG Score"
    }
    units = {
        "emissions": "tCO2e",
        "energy": "MWh",
        "water": "m³",
        "waste": "%",
        "social": "score"
    }
    
    # Sample values
    values = {
        "emissions": [120, 110, 105, 100, 95, 90],
        "energy": [1500, 1450, 1400, 1350, 1300, 1250],
        "water": [450, 440, 430, 420, 410, 400],
        "waste": [60, 65, 70, 75, 80, 85],
        "social": [70, 72, 74, 76, 78, 80]
    }
    
    # Generate metrics for past 6 months
    for month in range(6):
        # Set date to the first day of each month, starting 6 months ago
        from_date = datetime.now()
        month_date = datetime(from_date.year, from_date.month - month if from_date.month > month else from_date.month - month + 12, 1)
        timestamp = month_date.isoformat()
        
        for category in categories:
            metrics.append({
                "name": names[category],
                "category": category,
                "value": values[category][month],
                "unit": units[category],
                "timestamp": timestamp
            })
    
    return metrics

def run_all_tests():
    """Run all tests and return overall success"""
    print("\n")
    print("🚀 Starting Tests...\n")
    
    results = {}
    
    # Test dashboard page
    results["dashboard"] = test_frontend_dashboard()
    print("\n")
    
    # Test frontend proxy endpoints
    results["frontend_predictive"] = test_predictive_analytics_endpoint(direct=False)
    print("\n")
    results["frontend_materiality"] = test_materiality_assessment_endpoint(direct=False)
    print("\n")
    
    # Test backend direct endpoints (if backend is running)
    try:
        backend_health = requests.get(f"{FASTAPI_URL}/health", timeout=5)
        if backend_health.status_code == 200:
            results["backend_predictive"] = test_predictive_analytics_endpoint(direct=True)
            print("\n")
            results["backend_materiality"] = test_materiality_assessment_endpoint(direct=True)
            print("\n")
        else:
            print("⚠️ Backend API not available, skipping direct endpoint tests")
            results["backend_predictive"] = None
            results["backend_materiality"] = None
    except Exception:
        print("⚠️ Backend API not available, skipping direct endpoint tests")
        results["backend_predictive"] = None
        results["backend_materiality"] = None
    
    # Print test summary
    print("\n============ Test Summary ============")
    for test, result in results.items():
        status = "✅ PASSED" if result is True else "❌ FAILED" if result is False else "⚠️ SKIPPED"
        print(f"{test.replace('_', ' ').title()}: {status}")
    
    # Overall result
    frontend_tests = [results["dashboard"], results["frontend_predictive"], results["frontend_materiality"]]
    backend_tests = [results["backend_predictive"], results["backend_materiality"]]
    frontend_success = all(result for result in frontend_tests if result is not None)
    backend_available = any(result is not None for result in backend_tests)
    backend_success = all(result for result in backend_tests if result is not None)
    
    print("\n============ Overall Result ============")
    print(f"Frontend Tests: {'✅ PASSED' if frontend_success else '❌ FAILED'}")
    if backend_available:
        print(f"Backend Tests: {'✅ PASSED' if backend_success else '❌ FAILED'}")
    else:
        print("Backend Tests: ⚠️ SKIPPED (Backend not available)")
    
    overall = frontend_success and (not backend_available or backend_success)
    print(f"Overall: {'✅ PASSED' if overall else '❌ FAILED'}")
    
    return overall

if __name__ == "__main__":
    try:
        success = run_all_tests()
        print("\nTests completed.")
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\nTests interrupted by user.")
        sys.exit(130)
    except Exception as e:
        print(f"\nUnexpected error during testing: {str(e)}")
        sys.exit(1)
