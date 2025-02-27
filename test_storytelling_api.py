#!/usr/bin/env python3
"""
Test script for the storytelling API
This script tests the functionality of the FastAPI storytelling backend
"""
import os
import sys
import json
import requests
import time
import subprocess
import signal

def start_api_server():
    """Start the FastAPI server in a subprocess"""
    print("Starting FastAPI storytelling backend...")
    
    # Run the FastAPI server script
    process = subprocess.Popen(['python', 'run-storytelling-api.py'], 
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE,
                              text=True)
    
    # Give the server some time to start up
    time.sleep(5)
    
    return process

def test_health_endpoint(base_url):
    """Test the health check endpoint"""
    print("\n========= Testing Health Check Endpoint =========")
    
    try:
        response = requests.get(f"{base_url}/health")
        print(f"Status code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        return response.status_code == 200
    except Exception as e:
        print(f"Error testing health check endpoint: {str(e)}")
        return False

def test_storytelling_endpoint(base_url):
    """Test the storytelling endpoint"""
    print("\n========= Testing Storytelling Endpoint =========")
    
    # Test company and industry
    company_name = "EcoTech Solutions"
    industry = "Technology"
    
    print(f"Generating sustainability story for {company_name} in {industry} industry...")
    
    try:
        response = requests.post(
            f"{base_url}/api/sustainability-story",
            params={"company_name": company_name, "industry": industry},
            timeout=30.0
        )
        
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("Successfully received sustainability story")
            
            # Print the result in a formatted way
            print("\n========= Generated Story =========")
            print(json.dumps(result, indent=2)[:500] + "... (truncated)")
            
            # Verify the structure of the result
            expected_keys = [
                "Company", "Industry", "Industry_Context", "Sustainability_Strategy",
                "Competitor_Benchmarking", "Monetization_Model", "Investment_Pathway",
                "Actionable_Recommendations"
            ]
            
            missing_keys = [key for key in expected_keys if key not in result]
            if missing_keys:
                print(f"\nWARNING: The following expected keys are missing from the result: {missing_keys}")
            else:
                print("\nAll expected keys are present in the result")
            
            return True
        else:
            print(f"Error: Received status code {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"Error testing storytelling endpoint: {str(e)}")
        return False

def main():
    """Main test function"""
    # Set base URL for API
    base_url = "http://localhost:8080"
    
    # Start the API server
    api_process = start_api_server()
    
    try:
        # Test the health endpoint
        health_success = test_health_endpoint(base_url)
        
        if health_success:
            # Test the storytelling endpoint
            storytelling_success = test_storytelling_endpoint(base_url)
        else:
            storytelling_success = False
        
        # Print overall results
        print("\n========= Test Results =========")
        print("Health check test:", "PASSED" if health_success else "FAILED")
        print("Storytelling test:", "PASSED" if storytelling_success else "FAILED")
        print("Overall test:", "PASSED" if (health_success and storytelling_success) else "FAILED")
        
    finally:
        # Terminate the API server
        print("\nShutting down API server...")
        api_process.terminate()
        api_process.wait(timeout=5)

if __name__ == "__main__":
    main()
