#!/usr/bin/env python3
"""
Test script for the integrated sustainability platform
This script tests the integration between the Flask frontend and FastAPI backend
"""
import os
import sys
import json
import requests
import time
import subprocess
import signal
import webbrowser

def start_platform():
    """Start both the Flask frontend and FastAPI backend"""
    print("Starting integrated sustainability platform...")
    
    # Run the integrated platform script
    process = subprocess.Popen(['bash', 'run-sustainability-platform.sh'], 
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE,
                              text=True)
    
    # Give the services some time to start up
    time.sleep(10)
    
    return process

def test_backend_health(backend_url):
    """Test the FastAPI backend health check"""
    print("\n========= Testing Backend Health =========")
    
    try:
        response = requests.get(f"{backend_url}/health")
        print(f"Status code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        return response.status_code == 200
    except Exception as e:
        print(f"Error testing backend health: {str(e)}")
        return False

def test_frontend_home(frontend_url):
    """Test the Flask frontend home page"""
    print("\n========= Testing Frontend Home Page =========")
    
    try:
        response = requests.get(frontend_url)
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            print("Successfully loaded frontend home page")
            return True
        else:
            print(f"Error: Received status code {response.status_code}")
            return False
    except Exception as e:
        print(f"Error testing frontend home page: {str(e)}")
        return False

def test_frontend_stories_page(frontend_url):
    """Test the Flask frontend stories page"""
    print("\n========= Testing Frontend Stories Page =========")
    
    try:
        response = requests.get(f"{frontend_url}/sustainability-stories")
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            print("Successfully loaded sustainability stories page")
            return True
        else:
            print(f"Error: Received status code {response.status_code}")
            return False
    except Exception as e:
        print(f"Error testing sustainability stories page: {str(e)}")
        return False

def test_integrated_storytelling(frontend_url, backend_url):
    """Test the integrated storytelling functionality"""
    print("\n========= Testing Integrated Storytelling =========")
    
    # Test company and industry
    company_name = "GreenBuild Construction"
    industry = "Construction"
    
    print(f"Generating sustainability story through frontend proxy for {company_name} in {industry} industry...")
    
    try:
        # First verify the backend direct API works
        backend_response = requests.post(
            f"{backend_url}/api/sustainability-story",
            params={"company_name": company_name, "industry": industry},
            timeout=30.0
        )
        
        if backend_response.status_code != 200:
            print(f"Backend API failed with status code {backend_response.status_code}")
            print(f"Response: {backend_response.text}")
            return False
        
        # Now test the frontend proxy
        frontend_response = requests.post(
            f"{frontend_url}/api/storytelling",
            json={"company_name": company_name, "industry": industry},
            timeout=30.0
        )
        
        print(f"Frontend proxy status code: {frontend_response.status_code}")
        
        if frontend_response.status_code == 200:
            result = frontend_response.json()
            print("Successfully received sustainability story through frontend proxy")
            
            # Print the result in a formatted way
            print("\n========= Generated Story Through Frontend =========")
            print(json.dumps(result, indent=2)[:500] + "... (truncated)")
            
            # Verify the structure of the result
            expected_keys = [
                "Company", "Industry", "Sustainability_Strategy", 
                "Monetization_Model", "Investment_Pathway", 
                "Actionable_Recommendations"
            ]
            
            missing_keys = [key for key in expected_keys if key not in result]
            if missing_keys:
                print(f"\nWARNING: The following expected keys are missing from the result: {missing_keys}")
            else:
                print("\nAll expected keys are present in the result")
            
            return True
        else:
            print(f"Error: Received status code {frontend_response.status_code}")
            print(f"Response: {frontend_response.text}")
            return False
    except Exception as e:
        print(f"Error testing integrated storytelling: {str(e)}")
        return False

def main():
    """Main test function"""
    # Set URLs for frontend and backend
    frontend_url = "http://localhost:5000"
    backend_url = "http://localhost:8080"
    
    # Start the integrated platform
    platform_process = start_platform()
    
    try:
        # Output from the platform process
        print("\n========= Platform Startup Output =========")
        for i in range(10):  # Read a few lines of output
            out_line = platform_process.stdout.readline().strip()
            err_line = platform_process.stderr.readline().strip()
            if out_line:
                print(f"STDOUT: {out_line}")
            if err_line:
                print(f"STDERR: {err_line}")
        
        # Test backend health
        backend_health = test_backend_health(backend_url)
        
        # Test frontend pages
        frontend_home = test_frontend_home(frontend_url)
        frontend_stories = test_frontend_stories_page(frontend_url)
        
        # Test integrated storytelling if other tests passed
        if backend_health and frontend_home and frontend_stories:
            integrated_storytelling = test_integrated_storytelling(frontend_url, backend_url)
        else:
            integrated_storytelling = False
        
        # Print overall results
        print("\n========= Test Results =========")
        print("Backend health test:", "PASSED" if backend_health else "FAILED")
        print("Frontend home test:", "PASSED" if frontend_home else "FAILED")
        print("Frontend stories test:", "PASSED" if frontend_stories else "FAILED")
        print("Integrated storytelling test:", "PASSED" if integrated_storytelling else "FAILED")
        print("Overall test:", "PASSED" if (backend_health and frontend_home and frontend_stories and integrated_storytelling) else "FAILED")
        
        # Open browser to view the application if tests passed
        if backend_health and frontend_home and frontend_stories:
            print("\nOpening browser to view the application...")
            webbrowser.open(f"{frontend_url}/sustainability-stories")
            
    finally:
        # Terminate the platform process
        print("\nShutting down integrated platform...")
        platform_process.terminate()
        platform_process.wait(timeout=5)

if __name__ == "__main__":
    main()
