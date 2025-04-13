"""
Example of using AI-powered code automation for sustainability data extraction and processing

This script demonstrates how to use the AI-powered code automation utilities
in the SustainaTrend™ platform for:
1. Extracting sustainability data from various sources
2. Optimizing data processing functions
3. Generating comprehensive unit tests
"""
import os
import sys
import json
import logging
import requests
from typing import Dict, Any, List, Optional

# Add backend to path if it's not already there
backend_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backend')
if backend_path not in sys.path:
    sys.path.append(backend_path)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Try to import AI code automation utilities from backend
try:
    from backend.utils.ai_code_automation import (
        optimize_function, 
        generate_unit_tests, 
        suggest_code_improvements, 
        extract_sustainability_data
    )
    from backend.utils.fixed_test_generator import SustainabilityTestGenerator
    HAS_AI_CODE_AUTOMATION = True
    logger.info("AI code automation utilities loaded successfully")
except ImportError as e:
    HAS_AI_CODE_AUTOMATION = False
    logger.warning(f"AI code automation utilities not available: {e}")
    
def original_extract_esg_metrics(api_endpoint):
    """
    Extract ESG metrics from the specified API endpoint.
    This is a simple implementation that could be optimized by AI.
    
    Args:
        api_endpoint: URL of the API endpoint to fetch data from
        
    Returns:
        Dictionary containing ESG metrics
    """
    try:
        # Make the request
        response = requests.get(api_endpoint)
        
        # Check if request was successful
        if response.status_code == 200:
            data = response.json()
            
            # Extract metrics
            metrics = {}
            if 'carbonEmissions' in data:
                metrics['emissions'] = data['carbonEmissions']
            if 'waterUsage' in data:
                metrics['water'] = data['waterUsage']
            if 'energyConsumption' in data:
                metrics['energy'] = data['energyConsumption']
            if 'wasteGenerated' in data:
                metrics['waste'] = data['wasteGenerated']
            
            return {
                'status': 'success',
                'metrics': metrics
            }
        else:
            return {
                'status': 'error',
                'message': f'API request failed with status code {response.status_code}'
            }
    except Exception as e:
        return {
            'status': 'error',
            'message': str(e)
        }

def analyze_carbon_emissions(metrics_data):
    """
    Analyze carbon emissions data to identify trends and patterns.
    This is a simple implementation that could be optimized by AI.
    
    Args:
        metrics_data: List of carbon emissions metrics over time
        
    Returns:
        Dictionary containing analysis results
    """
    if not metrics_data:
        return {
            'status': 'error',
            'message': 'No metrics data provided'
        }
    
    try:
        # Extract values and dates
        values = [item['value'] for item in metrics_data if 'value' in item]
        dates = [item['date'] for item in metrics_data if 'date' in item]
        
        if not values or len(values) != len(dates):
            return {
                'status': 'error',
                'message': 'Invalid metrics data format'
            }
        
        # Calculate basic statistics
        average = sum(values) / len(values)
        minimum = min(values)
        maximum = max(values)
        
        # Determine trend (simple approach)
        if len(values) > 1:
            first_half = sum(values[:len(values)//2]) / (len(values)//2)
            second_half = sum(values[len(values)//2:]) / (len(values) - len(values)//2)
            
            if second_half < first_half:
                trend = 'decreasing'
            elif second_half > first_half:
                trend = 'increasing'
            else:
                trend = 'stable'
        else:
            trend = 'unknown'
        
        return {
            'status': 'success',
            'average': average,
            'minimum': minimum,
            'maximum': maximum,
            'trend': trend,
            'data_points': len(values)
        }
    except Exception as e:
        return {
            'status': 'error',
            'message': str(e)
        }

def main():
    """
    Main function to demonstrate AI-powered code automation
    """
    logger.info("Demonstrating AI-powered code automation")
    
    # Example 1: Optimizing an existing function
    if HAS_AI_CODE_AUTOMATION:
        logger.info("Example 1: Optimizing an existing function")
        
        # Get the original function code
        original_code = inspect.getsource(original_extract_esg_metrics)
        
        # Optimize the function for efficiency
        optimized_code = optimize_function(
            original_code, 
            optimization_goal="efficiency", 
            context="sustainability"
        )
        
        print("\n=== Original Function ===")
        print(original_code)
        
        print("\n=== AI-Optimized Function ===")
        print(optimized_code)
    else:
        logger.warning("Skipping Example 1: AI code automation not available")
    
    # Example 2: Generating comprehensive tests
    if HAS_AI_CODE_AUTOMATION:
        logger.info("Example 2: Generating comprehensive tests")
        
        # Get the original function code
        original_code = inspect.getsource(analyze_carbon_emissions)
        
        # Create a test generator instance
        test_generator = SustainabilityTestGenerator(test_framework="pytest")
        
        # Generate tests for the function
        tests = test_generator.generate_test_for_function(original_code)
        
        print("\n=== Original Function ===")
        print(original_code)
        
        print("\n=== AI-Generated Tests ===")
        print(tests)
    else:
        logger.warning("Skipping Example 2: AI code automation not available")
    
    # Example 3: Getting code improvement suggestions
    if HAS_AI_CODE_AUTOMATION:
        logger.info("Example 3: Getting code improvement suggestions")
        
        # Get the original function code
        original_code = inspect.getsource(original_extract_esg_metrics)
        
        # Get improvement suggestions
        suggestions = suggest_code_improvements(
            original_code, 
            improvement_type="all"
        )
        
        print("\n=== Code Improvement Suggestions ===")
        for i, suggestion in enumerate(suggestions, 1):
            print(f"{i}. {suggestion['suggestion']}")
            print(f"   Issue: {suggestion['issue']}")
            print(f"   Explanation: {suggestion['explanation']}")
            print()
    else:
        logger.warning("Skipping Example 3: AI code automation not available")

if __name__ == "__main__":
    try:
        import inspect  # Import here to avoid circular import issues
        main()
    except Exception as e:
        logger.error(f"Error in main function: {str(e)}")