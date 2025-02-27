#!/usr/bin/env python3
"""
Test script for the storytelling AI module
This script tests the functionality of the storytelling_ai module directly
"""
import os
import sys
import json

# Set the Python path to include the backend directory
backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend")
sys.path.insert(0, backend_dir)

# Import the storytelling_ai module
try:
    from services.storytelling_ai import generate_sustainability_story
    print("Successfully imported storytelling_ai module")
except ImportError as e:
    print(f"Error importing storytelling_ai module: {str(e)}")
    sys.exit(1)

def test_storytelling_ai():
    """Test the storytelling AI module directly"""
    print("\n========= Testing Storytelling AI Module =========")
    
    # Test company and industry
    company_name = "EcoTech Solutions"
    industry = "Technology"
    
    print(f"Generating sustainability story for {company_name} in {industry} industry...")
    
    # Call the generate_sustainability_story function
    try:
        result = generate_sustainability_story(company_name, industry)
        print("Successfully generated sustainability story")
        
        # Print the result in a formatted way
        print("\n========= Generated Story =========")
        print(json.dumps(result, indent=2))
        
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
    except Exception as e:
        print(f"Error generating sustainability story: {str(e)}")
        return False

if __name__ == "__main__":
    # Set the OpenAI API key from environment variable if available
    api_key = os.getenv('OPENAI_API_KEY')
    print(f"OpenAI API key is {'available' if api_key else 'NOT available'}")
    
    # Run the test
    success = test_storytelling_ai()
    print("\n========= Test Result =========")
    print("Storytelling AI test:", "PASSED" if success else "FAILED")
