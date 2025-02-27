#!/usr/bin/env python
"""
Test script for the AI-powered predictive analytics functionality in the sustainability platform API.
"""
import os
import sys
import json
import time
import subprocess
import requests
from datetime import datetime, timedelta
import random

# Constants
API_URL = "http://localhost:8080"
TEST_COMPANY = "EcoTech Solutions"
TEST_INDUSTRY = "Technology"

def start_api_server():
    """Start the FastAPI server for testing"""
    print("Starting FastAPI predictive analytics backend...")
    
    # Start the API server
    process = subprocess.Popen(
        ["python", "backend/storytelling_api.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait for server to start
    time.sleep(5)
    
    return process

def stop_api_server(process):
    """Stop the API server"""
    print("Shutting down API server...")
    process.terminate()
    process.wait()

def test_health_check():
    """Test the health check endpoint"""
    print("\n========= Testing Health Check Endpoint =========")
    response = requests.get(f"{API_URL}/health")
    print(f"Status code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    return response.status_code == 200

def test_predictive_analytics():
    """Test the predictive analytics endpoint"""
    print("\n========= Testing Predictive Analytics Endpoint =========")
    
    # Generate sample metrics data
    metrics = generate_sample_metrics()
    
    # Test parameters
    params = {
        "company_name": TEST_COMPANY,
        "industry": TEST_INDUSTRY,
        "forecast_periods": 3
    }
    
    print(f"Generating predictive analytics for {TEST_COMPANY} in {TEST_INDUSTRY} industry...")
    response = requests.post(
        f"{API_URL}/api/predictive-analytics",
        params=params,
        json=metrics
    )
    
    print(f"Status code: {response.status_code}")
    
    if response.status_code == 200:
        print("Successfully received predictive analytics")
        
        # Print a truncated version of the response for readability
        result = response.json()
        print("\n========= Generated Predictions =========")
        print(json.dumps(result, indent=2)[:500] + "... (truncated)")
        
        # Verify the result has all expected keys
        expected_keys = ["forecast_date", "forecast_periods", "predictions", "ai_insights"]
        missing_keys = [key for key in expected_keys if key not in result]
        
        if not missing_keys:
            print("\nAll expected keys are present in the result")
            
            # Check if we have at least one prediction
            predictions = result.get("predictions", [])
            if predictions:
                print(f"Received {len(predictions)} predictions")
                
                # Check prediction structure
                prediction = predictions[0]
                prediction_keys = ["name", "category", "current_value", "predicted_values", 
                                 "confidence_intervals", "trend_direction", "trend_strength"]
                missing_prediction_keys = [key for key in prediction_keys if key not in prediction]
                
                if not missing_prediction_keys:
                    print("Prediction structure is valid")
                    return True
                else:
                    print(f"Prediction is missing these keys: {missing_prediction_keys}")
            else:
                print("No predictions received")
        else:
            print(f"Response is missing these keys: {missing_keys}")
    
    return False

def test_materiality_assessment():
    """Test the materiality assessment endpoint"""
    print("\n========= Testing Materiality Assessment Endpoint =========")
    
    # Test parameters
    params = {
        "company_name": TEST_COMPANY,
        "industry": TEST_INDUSTRY
    }
    
    print(f"Performing materiality assessment for {TEST_COMPANY} in {TEST_INDUSTRY} industry...")
    response = requests.post(
        f"{API_URL}/api/materiality-assessment",
        params=params
    )
    
    print(f"Status code: {response.status_code}")
    
    if response.status_code == 200:
        print("Successfully received materiality assessment")
        
        # Print a truncated version of the response for readability
        result = response.json()
        print("\n========= Materiality Assessment =========")
        print(json.dumps(result, indent=2)[:500] + "... (truncated)")
        
        # Verify the result has all expected keys
        expected_keys = ["company", "industry", "assessment_date", "material_topics"]
        missing_keys = [key for key in expected_keys if key not in result]
        
        if not missing_keys:
            print("\nAll expected keys are present in the result")
            
            # Check if we have at least one material topic
            topics = result.get("material_topics", [])
            if topics:
                print(f"Received {len(topics)} material topics")
                
                # Check topic structure
                topic = topics[0]
                topic_keys = ["topic", "business_impact_score", "stakeholder_concern_score", 
                             "materiality_score", "financial_impact", "recommended_metrics"]
                missing_topic_keys = [key for key in topic_keys if key not in topic]
                
                if not missing_topic_keys:
                    print("Material topic structure is valid")
                    return True
                else:
                    print(f"Material topic is missing these keys: {missing_topic_keys}")
            else:
                print("No material topics received")
        else:
            print(f"Response is missing these keys: {missing_keys}")
    
    return False

def generate_sample_metrics():
    """Generate sample metrics data for testing"""
    # Define metric templates
    metric_templates = [
        {
            "name": "Carbon Emissions",
            "category": "emissions",
            "unit": "tCO2e"
        },
        {
            "name": "Energy Consumption",
            "category": "energy",
            "unit": "MWh"
        },
        {
            "name": "Water Usage",
            "category": "water",
            "unit": "m³"
        },
        {
            "name": "Waste Recycled",
            "category": "waste",
            "unit": "%"
        },
        {
            "name": "ESG Score",
            "category": "social",
            "unit": "score"
        }
    ]
    
    # Generate metrics for the past 12 months
    metrics = []
    end_date = datetime.now()
    
    for i in range(12):
        date = end_date - timedelta(days=30 * i)
        timestamp = date.isoformat()
        
        for template in metric_templates:
            # For emissions, energy, and water, lower is better, so have a downward trend
            if template["name"] in ["Carbon Emissions", "Energy Consumption", "Water Usage"]:
                # Start with a higher value and decrease (with some noise)
                base_value = 100 - (i * 3)
                noise = random.uniform(-5, 5)
                value = base_value + noise
            else:
                # For ESG score and recycling, higher is better, so have an upward trend
                base_value = 50 + (i * 2)
                noise = random.uniform(-3, 3)
                value = base_value + noise
            
            # Ensure values are positive
            value = max(0, value)
            
            metric = {
                "name": template["name"],
                "category": template["category"],
                "value": value,
                "unit": template["unit"],
                "timestamp": timestamp
            }
            
            metrics.append(metric)
    
    return metrics

def main():
    """Main test function"""
    try:
        # Start the API server
        api_process = start_api_server()
        
        # Run the tests
        health_test_passed = test_health_check()
        predictive_test_passed = test_predictive_analytics()
        materiality_test_passed = test_materiality_assessment()
        
        # Print test results
        print("\n========= Test Results =========")
        print(f"Health check test: {'PASSED' if health_test_passed else 'FAILED'}")
        print(f"Predictive analytics test: {'PASSED' if predictive_test_passed else 'FAILED'}")
        print(f"Materiality assessment test: {'PASSED' if materiality_test_passed else 'FAILED'}")
        print(f"Overall test: {'PASSED' if all([health_test_passed, predictive_test_passed, materiality_test_passed]) else 'FAILED'}")
        
    finally:
        # Stop the API server
        stop_api_server(api_process)

if __name__ == "__main__":
    main()
