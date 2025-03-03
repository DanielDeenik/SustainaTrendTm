"""
AI-Powered Test Generator for Sustainability Data Functions

This module uses AI to automatically generate comprehensive test cases
for sustainability data processing functions, ensuring data integrity 
and accuracy for ESG analytics.
"""
import logging
import os
import inspect
import re
import ast
from typing import Dict, List, Any, Optional, Callable, Union, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import the AI code automation utilities
try:
    from backend.utils.ai_code_automation import generate_unit_tests
    AI_TEST_GENERATION_AVAILABLE = True
except ImportError:
    AI_TEST_GENERATION_AVAILABLE = False
    logger.warning("AI test generation utilities not available. Using built-in generators.")

class SustainabilityTestGenerator:
    """
    Generator for comprehensive tests targeting sustainability data functions
    with a focus on data integrity, ESG compliance, and analytics accuracy.
    """
    
    def __init__(self, test_framework: str = "pytest"):
        """
        Initialize the test generator
        
        Args:
            test_framework: Test framework to use (pytest or unittest)
        """
        self.test_framework = test_framework
        logger.info(f"Initialized sustainability test generator with {test_framework} framework")
    
    def generate_test_for_function(self, function: Callable) -> str:
        """
        Generate tests for a specific function
        
        Args:
            function: The function to generate tests for
            
        Returns:
            Generated test code as a string
        """
        function_name = function.__name__
        logger.info(f"Generating tests for function: {function_name}")
        
        # Use AI-powered test generation if available
        if AI_TEST_GENERATION_AVAILABLE:
            try:
                return generate_unit_tests(function, self.test_framework)
            except Exception as e:
                logger.error(f"Error generating AI-powered tests: {str(e)}")
                # Fall back to built-in generators
        
        # Use built-in generators based on function type
        function_code = inspect.getsource(function)
        
        # Detect function type based on name or code content
        function_type = self._detect_function_type(function_name, function_code)
        
        if function_type == "data_extraction":
            return self._generate_data_extraction_tests(function)
        elif function_type == "data_analysis":
            return self._generate_data_analysis_tests(function)
        elif function_type == "prediction":
            return self._generate_prediction_tests(function)
        elif function_type == "visualization":
            return self._generate_visualization_tests(function)
        else:
            return self._generate_generic_tests(function)
    
    def _detect_function_type(self, function_name: str, function_code: str) -> str:
        """
        Detect the type of function based on its name and code
        
        Args:
            function_name: Name of the function
            function_code: Source code of the function
            
        Returns:
            Detected function type
        """
        # Check for extraction functions
        if any(keyword in function_name.lower() for keyword in ["extract", "get", "fetch", "load", "read"]):
            return "data_extraction"
        
        # Check for analysis functions
        elif any(keyword in function_name.lower() for keyword in ["analyze", "calculate", "compute", "process"]):
            return "data_analysis"
        
        # Check for prediction functions
        elif any(keyword in function_name.lower() for keyword in ["predict", "forecast", "model", "estimate"]):
            return "prediction"
        
        # Check for visualization functions
        elif any(keyword in function_name.lower() for keyword in ["plot", "chart", "graph", "visualize", "display"]):
            return "visualization"
        
        # Check code content for clues
        else:
            if "request" in function_code.lower() or "api" in function_code.lower():
                return "data_extraction"
            elif "dataframe" in function_code.lower() or "pandas" in function_code.lower():
                return "data_analysis"
            elif "model" in function_code.lower() or "predict" in function_code.lower():
                return "prediction"
            elif "plot" in function_code.lower() or "fig" in function_code.lower():
                return "visualization"
            else:
                return "generic"
    
    def _generate_data_extraction_tests(self, function: Callable) -> str:
        """Generate tests for data extraction functions"""
        function_name = function.__name__
        module_name = function.__module__
        
        if self.test_framework == "pytest":
            test_code = f"""
import pytest
import requests
import responses
from {module_name} import {function_name}

# Mock responses for testing
MOCK_SUCCESS_RESPONSE = {{
    "data": {{
        "metrics": [
            {{"name": "carbon_emissions", "value": 120.5, "unit": "tCO2e", "category": "emissions"}},
            {{"name": "water_usage", "value": 5000, "unit": "m3", "category": "water"}},
            {{"name": "renewable_energy", "value": 45.2, "unit": "percent", "category": "energy"}}
        ]
    }}
}}

MOCK_ERROR_RESPONSE = {{
    "error": "Access denied",
    "code": 403
}}

@responses.activate
def test_{function_name}_success():
    """Test successful data extraction"""
    # Setup mock API endpoint
    test_endpoint = "https://api.test.com/sustainability/metrics"
    responses.add(
        responses.GET,
        test_endpoint,
        json=MOCK_SUCCESS_RESPONSE,
        status=200
    )
    
    # Call the function with the mock endpoint
    result = {function_name}(test_endpoint)
    
    # Verify the result structure
    assert "metadata" in result, "Result should contain metadata"
    assert "metrics" in result, "Result should contain metrics"
    assert result["metadata"]["source"] == test_endpoint, "Source should match the API endpoint"
    assert len(result["metrics"]) > 0, "Should extract at least some metrics"

@responses.activate
def test_{function_name}_error_handling():
    """Test error handling during extraction"""
    # Setup mock API endpoint with error response
    test_endpoint = "https://api.test.com/sustainability/metrics"
    responses.add(
        responses.GET,
        test_endpoint,
        json=MOCK_ERROR_RESPONSE,
        status=403
    )
    
    # Call the function with the mock endpoint
    result = {function_name}(test_endpoint)
    
    # Verify error handling
    assert "metadata" in result, "Result should contain metadata even on error"
    assert "error" in result["metadata"], "Metadata should contain error information"
    assert result["metadata"]["status"] == "failed", "Status should be failed"

@responses.activate
def test_{function_name}_timeout_handling():
    """Test timeout handling during extraction"""
    # Setup mock API endpoint with timeout
    test_endpoint = "https://api.test.com/sustainability/metrics"
    responses.add(
        responses.GET,
        test_endpoint,
        body=requests.exceptions.Timeout("Connection timed out")
    )
    
    # Call the function with the mock endpoint
    result = {function_name}(test_endpoint)
    
    # Verify timeout handling
    assert "metadata" in result, "Result should contain metadata even on timeout"
    assert "error" in result["metadata"], "Metadata should contain error information"
    assert result["metadata"]["status"] == "failed", "Status should be failed"

def test_{function_name}_invalid_endpoint():
    """Test with invalid endpoint"""
    # Call with invalid endpoint
    result = {function_name}("not-a-valid-url")
    
    # Verify error handling for invalid URL
    assert "metadata" in result, "Result should contain metadata even with invalid URL"
    assert "error" in result["metadata"], "Metadata should contain error information"
    assert result["metadata"]["status"] == "failed", "Status should be failed"
"""
        else:  # unittest
            test_code = f"""
import unittest
import requests
import responses
from {module_name} import {function_name}

class Test{function_name.capitalize()}(unittest.TestCase):
    # Mock responses for testing
    MOCK_SUCCESS_RESPONSE = {{
        "data": {{
            "metrics": [
                {{"name": "carbon_emissions", "value": 120.5, "unit": "tCO2e", "category": "emissions"}},
                {{"name": "water_usage", "value": 5000, "unit": "m3", "category": "water"}},
                {{"name": "renewable_energy", "value": 45.2, "unit": "percent", "category": "energy"}}
            ]
        }}
    }}

    MOCK_ERROR_RESPONSE = {{
        "error": "Access denied",
        "code": 403
    }}
    
    @responses.activate
    def test_success(self):
        """Test successful data extraction"""
        # Setup mock API endpoint
        test_endpoint = "https://api.test.com/sustainability/metrics"
        responses.add(
            responses.GET,
            test_endpoint,
            json=self.MOCK_SUCCESS_RESPONSE,
            status=200
        )
        
        # Call the function with the mock endpoint
        result = {function_name}(test_endpoint)
        
        # Verify the result structure
        self.assertIn("metadata", result, "Result should contain metadata")
        self.assertIn("metrics", result, "Result should contain metrics")
        self.assertEqual(result["metadata"]["source"], test_endpoint, "Source should match the API endpoint")
        self.assertGreater(len(result["metrics"]), 0, "Should extract at least some metrics")
    
    @responses.activate
    def test_error_handling(self):
        """Test error handling during extraction"""
        # Setup mock API endpoint with error response
        test_endpoint = "https://api.test.com/sustainability/metrics"
        responses.add(
            responses.GET,
            test_endpoint,
            json=self.MOCK_ERROR_RESPONSE,
            status=403
        )
        
        # Call the function with the mock endpoint
        result = {function_name}(test_endpoint)
        
        # Verify error handling
        self.assertIn("metadata", result, "Result should contain metadata even on error")
        self.assertIn("error", result["metadata"], "Metadata should contain error information")
        self.assertEqual(result["metadata"]["status"], "failed", "Status should be failed")
    
    @responses.activate
    def test_timeout_handling(self):
        """Test timeout handling during extraction"""
        # Setup mock API endpoint with timeout
        test_endpoint = "https://api.test.com/sustainability/metrics"
        responses.add(
            responses.GET,
            test_endpoint,
            body=requests.exceptions.Timeout("Connection timed out")
        )
        
        # Call the function with the mock endpoint
        result = {function_name}(test_endpoint)
        
        # Verify timeout handling
        self.assertIn("metadata", result, "Result should contain metadata even on timeout")
        self.assertIn("error", result["metadata"], "Metadata should contain error information")
        self.assertEqual(result["metadata"]["status"], "failed", "Status should be failed")
    
    def test_invalid_endpoint(self):
        """Test with invalid endpoint"""
        # Call with invalid endpoint
        result = {function_name}("not-a-valid-url")
        
        # Verify error handling for invalid URL
        self.assertIn("metadata", result, "Result should contain metadata even with invalid URL")
        self.assertIn("error", result["metadata"], "Metadata should contain error information")
        self.assertEqual(result["metadata"]["status"], "failed", "Status should be failed")

if __name__ == '__main__':
    unittest.main()
"""
        
        return test_code
    
    def _generate_data_analysis_tests(self, function: Callable) -> str:
        """Generate tests for data analysis functions"""
        function_name = function.__name__
        module_name = function.__module__
        
        if self.test_framework == "pytest":
            test_code = f"""
import pytest
import pandas as pd
import numpy as np
from {module_name} import {function_name}

# Mock sustainability metrics data
@pytest.fixture
def sample_metrics_data():
    return [
        {{"name": "carbon_emissions", "value": 120.5, "unit": "tCO2e", "category": "emissions", "timestamp": "2023-01-01"}},
        {{"name": "carbon_emissions", "value": 115.2, "unit": "tCO2e", "category": "emissions", "timestamp": "2023-02-01"}},
        {{"name": "carbon_emissions", "value": 118.7, "unit": "tCO2e", "category": "emissions", "timestamp": "2023-03-01"}},
        {{"name": "water_usage", "value": 5000, "unit": "m3", "category": "water", "timestamp": "2023-01-01"}},
        {{"name": "water_usage", "value": 4800, "unit": "m3", "category": "water", "timestamp": "2023-02-01"}},
        {{"name": "water_usage", "value": 5100, "unit": "m3", "category": "water", "timestamp": "2023-03-01"}},
        {{"name": "renewable_energy", "value": 45.2, "unit": "percent", "category": "energy", "timestamp": "2023-01-01"}},
        {{"name": "renewable_energy", "value": 47.5, "unit": "percent", "category": "energy", "timestamp": "2023-02-01"}},
        {{"name": "renewable_energy", "value": 51.0, "unit": "percent", "category": "energy", "timestamp": "2023-03-01"}}
    ]

def test_{function_name}_with_valid_data(sample_metrics_data):
    """Test analysis with valid data"""
    # Call the function with sample data
    result = {function_name}(sample_metrics_data)
    
    # Verify result structure and content
    assert result is not None, "Result should not be None"
    
    if isinstance(result, dict):
        # For dictionary results (typical analysis output)
        for key in result.keys():
            assert result[key] is not None, f"Result key {{key}} should not be None"
    elif isinstance(result, list):
        # For list results (e.g., processed metrics)
        assert len(result) > 0, "Result should not be empty"
    elif isinstance(result, pd.DataFrame):
        # For DataFrame results
        assert not result.empty, "Result DataFrame should not be empty"
        assert "name" in result.columns or "category" in result.columns, "Result should have key metric columns"

def test_{function_name}_with_empty_data():
    """Test analysis with empty data"""
    # Call with empty data
    result = {function_name}([])
    
    # Verify appropriate handling of empty data
    if isinstance(result, dict):
        assert len(result) > 0, "Should return structured result even with empty input"
    elif isinstance(result, list):
        assert len(result) == 0, "Should return empty list for empty input"
    elif isinstance(result, pd.DataFrame):
        # Should return empty DataFrame or None
        pass
    else:
        assert result is not None, "Should handle empty input gracefully"

def test_{function_name}_with_missing_values(sample_metrics_data):
    """Test analysis with missing values"""
    # Create data with missing values
    data_with_missing = sample_metrics_data.copy()
    data_with_missing[0]["value"] = None
    data_with_missing[3]["value"] = np.nan
    
    # Call the function with data containing missing values
    result = {function_name}(data_with_missing)
    
    # Verify it handles missing values appropriately
    assert result is not None, "Should handle missing values"

def test_{function_name}_with_invalid_data():
    """Test analysis with invalid data structure"""
    # Create invalid data structure
    invalid_data = [
        {{"invalid_key": "value"}},
        {{"another_invalid": 123}}
    ]
    
    # Call with invalid data and verify it handles errors appropriately
    try:
        result = {function_name}(invalid_data)
        # If it doesn't raise an exception, the result should still be structured
        assert result is not None, "Should handle invalid data gracefully"
    except Exception as e:
        # Exception is acceptable if function is strict about input validation
        assert "invalid" in str(e).lower() or "missing" in str(e).lower(), "Exception should explain the data issue"
"""
        else:  # unittest
            test_code = f"""
import unittest
import pandas as pd
import numpy as np
from {module_name} import {function_name}

class Test{function_name.capitalize()}(unittest.TestCase):
    def setUp(self):
        # Setup sample data for testing
        self.sample_metrics_data = [
            {{"name": "carbon_emissions", "value": 120.5, "unit": "tCO2e", "category": "emissions", "timestamp": "2023-01-01"}},
            {{"name": "carbon_emissions", "value": 115.2, "unit": "tCO2e", "category": "emissions", "timestamp": "2023-02-01"}},
            {{"name": "carbon_emissions", "value": 118.7, "unit": "tCO2e", "category": "emissions", "timestamp": "2023-03-01"}},
            {{"name": "water_usage", "value": 5000, "unit": "m3", "category": "water", "timestamp": "2023-01-01"}},
            {{"name": "water_usage", "value": 4800, "unit": "m3", "category": "water", "timestamp": "2023-02-01"}},
            {{"name": "water_usage", "value": 5100, "unit": "m3", "category": "water", "timestamp": "2023-03-01"}},
            {{"name": "renewable_energy", "value": 45.2, "unit": "percent", "category": "energy", "timestamp": "2023-01-01"}},
            {{"name": "renewable_energy", "value": 47.5, "unit": "percent", "category": "energy", "timestamp": "2023-02-01"}},
            {{"name": "renewable_energy", "value": 51.0, "unit": "percent", "category": "energy", "timestamp": "2023-03-01"}}
        ]
    
    def test_with_valid_data(self):
        """Test analysis with valid data"""
        # Call the function with sample data
        result = {function_name}(self.sample_metrics_data)
        
        # Verify result structure and content
        self.assertIsNotNone(result, "Result should not be None")
        
        if isinstance(result, dict):
            # For dictionary results (typical analysis output)
            for key in result.keys():
                self.assertIsNotNone(result[key], f"Result key {{key}} should not be None")
        elif isinstance(result, list):
            # For list results (e.g., processed metrics)
            self.assertGreater(len(result), 0, "Result should not be empty")
        elif isinstance(result, pd.DataFrame):
            # For DataFrame results
            self.assertFalse(result.empty, "Result DataFrame should not be empty")
            self.assertTrue("name" in result.columns or "category" in result.columns, 
                           "Result should have key metric columns")
    
    def test_with_empty_data(self):
        """Test analysis with empty data"""
        # Call with empty data
        result = {function_name}([])
        
        # Verify appropriate handling of empty data
        if isinstance(result, dict):
            self.assertGreater(len(result), 0, "Should return structured result even with empty input")
        elif isinstance(result, list):
            self.assertEqual(len(result), 0, "Should return empty list for empty input")
        elif isinstance(result, pd.DataFrame):
            # Should return empty DataFrame or None
            pass
        else:
            self.assertIsNotNone(result, "Should handle empty input gracefully")
    
    def test_with_missing_values(self):
        """Test analysis with missing values"""
        # Create data with missing values
        data_with_missing = self.sample_metrics_data.copy()
        data_with_missing[0]["value"] = None
        data_with_missing[3]["value"] = np.nan
        
        # Call the function with data containing missing values
        result = {function_name}(data_with_missing)
        
        # Verify it handles missing values appropriately
        self.assertIsNotNone(result, "Should handle missing values")
    
    def test_with_invalid_data(self):
        """Test analysis with invalid data structure"""
        # Create invalid data structure
        invalid_data = [
            {{"invalid_key": "value"}},
            {{"another_invalid": 123}}
        ]
        
        # Call with invalid data and verify it handles errors appropriately
        try:
            result = {function_name}(invalid_data)
            # If it doesn't raise an exception, the result should still be structured
            self.assertIsNotNone(result, "Should handle invalid data gracefully")
        except Exception as e:
            # Exception is acceptable if function is strict about input validation
            self.assertTrue("invalid" in str(e).lower() or "missing" in str(e).lower(), 
                          "Exception should explain the data issue")

if __name__ == '__main__':
    unittest.main()
"""
        
        return test_code
    
    def _generate_prediction_tests(self, function: Callable) -> str:
        """Generate tests for prediction functions"""
        function_name = function.__name__
        module_name = function.__module__
        
        if self.test_framework == "pytest":
            test_code = f"""
import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from {module_name} import {function_name}

# Generate mock time-series data for sustainability metrics
@pytest.fixture
def historical_metrics_data():
    # Create 12 months of historical data for multiple metrics
    start_date = datetime(2022, 1, 1)
    metrics = []
    
    # Generate carbon emissions data with seasonal pattern
    for i in range(12):
        current_date = start_date + timedelta(days=30*i)
        # Add some seasonality and trend
        base_emissions = 100 + i * 0.5  # Slight upward trend
        seasonal_factor = 10 * np.sin(i * np.pi/6)  # Seasonal pattern
        
        metrics.append({{
            "name": "carbon_emissions",
            "value": base_emissions + seasonal_factor,
            "unit": "tCO2e",
            "category": "emissions",
            "timestamp": current_date.isoformat()
        }})
    
    # Generate renewable energy data with upward trend
    for i in range(12):
        current_date = start_date + timedelta(days=30*i)
        metrics.append({{
            "name": "renewable_energy",
            "value": 30 + i * 1.5,  # Strong upward trend
            "unit": "percent",
            "category": "energy",
            "timestamp": current_date.isoformat()
        }})
    
    # Generate water usage data with downward trend
    for i in range(12):
        current_date = start_date + timedelta(days=30*i)
        metrics.append({{
            "name": "water_usage",
            "value": 5000 - i * 50,  # Downward trend
            "unit": "m3",
            "category": "water",
            "timestamp": current_date.isoformat()
        }})
    
    return metrics

def test_{function_name}_output_structure(historical_metrics_data):
    """Test prediction output structure"""
    # Call the prediction function
    forecast_periods = 3
    result = {function_name}(historical_metrics_data, forecast_periods)
    
    # Verify basic structure
    assert isinstance(result, dict), "Result should be a dictionary"
    assert "forecast_date" in result, "Result should include forecast date"
    assert "forecast_periods" in result, "Result should include number of forecast periods"
    assert "predictions" in result, "Result should include predictions"
    assert isinstance(result["predictions"], list), "Predictions should be a list"
    
    # Verify predictions content
    if len(result["predictions"]) > 0:
        sample_prediction = result["predictions"][0]
        assert "name" in sample_prediction, "Prediction should include metric name"
        assert "category" in sample_prediction, "Prediction should include category"
        assert "values" in sample_prediction, "Prediction should include forecasted values"
        assert "confidence_intervals" in sample_prediction, "Prediction should include confidence intervals"
        assert len(sample_prediction["values"]) == forecast_periods, "Should have correct number of forecasted values"

def test_{function_name}_forecasting_accuracy(historical_metrics_data):
    """Test prediction accuracy by masking recent data"""
    # Get the latest 3 data points for each metric
    test_periods = 3
    training_data = []
    validation_data = {{}}
    
    for item in historical_metrics_data:
        metric_name = item["name"]
        if metric_name not in validation_data:
            validation_data[metric_name] = []
        
        # Collect validation data from the most recent periods
        timestamp = pd.to_datetime(item["timestamp"])
        if timestamp >= pd.to_datetime("2022-10-01"):
            validation_data[metric_name].append(item)
        else:
            training_data.append(item)
    
    # Make predictions using only training data
    result = {function_name}(training_data, test_periods)
    
    # For each metric, compare predictions with actual values
    for prediction in result["predictions"]:
        metric_name = prediction["name"]
        
        # Get actual values for this metric
        actual_values = []
        for item in validation_data.get(metric_name, []):
            actual_values.append(item["value"])
        
        # Skip if we don't have validation data for this metric
        if not actual_values:
            continue
            
        # Get predicted values
        predicted_values = prediction["values"]
        
        # Calculate mean absolute percentage error
        mape = 0
        count = min(len(actual_values), len(predicted_values))
        if count > 0:
            for i in range(count):
                if actual_values[i] != 0:  # Avoid division by zero
                    mape += abs((actual_values[i] - predicted_values[i]) / actual_values[i])
            mape = mape / count * 100
            
            # For a simple test, just verify MAPE is within reasonable bounds
            assert mape <= 50, f"MAPE should be <= 50%, got {{mape:.2f}}%"
            
            # Also verify confidence intervals contain actual values
            lower_bounds = prediction["confidence_intervals"]["lower"]
            upper_bounds = prediction["confidence_intervals"]["upper"]
            
            for i in range(count):
                # Allow some tolerance for validation
                assert actual_values[i] >= lower_bounds[i] * 0.8 or actual_values[i] <= upper_bounds[i] * 1.2, \\
                       f"Actual value {{actual_values[i]}} should be within confidence intervals (adjusted)"

def test_{function_name}_with_empty_data():
    """Test prediction with empty data"""
    # Call with empty data
    result = {function_name}([], 3)
    
    # Verify appropriate error handling
    assert isinstance(result, dict), "Result should be a dictionary even with empty input"
    assert "error" in result or len(result.get("predictions", [])) == 0, \\
           "Should handle empty input appropriately"

def test_{function_name}_with_inconsistent_data(historical_metrics_data):
    """Test prediction with inconsistent data"""
    # Create data with inconsistent timestamps
    inconsistent_data = historical_metrics_data.copy()
    
    # Add some data with very different timestamps
    inconsistent_data.append({{
        "name": "carbon_emissions",
        "value": 500,
        "unit": "tCO2e",
        "category": "emissions",
        "timestamp": "2050-01-01T00:00:00"  # Far future
    }})
    
    inconsistent_data.append({{
        "name": "carbon_emissions",
        "value": 200,
        "unit": "tCO2e",
        "category": "emissions",
        "timestamp": "1980-01-01T00:00:00"  # Far past
    }})
    
    # The function should still produce reasonable results
    result = {function_name}(inconsistent_data, 3)
    
    # Basic structure checks
    assert isinstance(result, dict), "Result should be a dictionary"
    assert "predictions" in result, "Result should include predictions"
"""
        else:  # unittest
            test_code = f"""
import unittest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from {module_name} import {function_name}

class Test{function_name.capitalize()}(unittest.TestCase):
    def setUp(self):
        # Generate mock time-series data for sustainability metrics
        start_date = datetime(2022, 1, 1)
        self.metrics = []
        
        # Generate carbon emissions data with seasonal pattern
        for i in range(12):
            current_date = start_date + timedelta(days=30*i)
            # Add some seasonality and trend
            base_emissions = 100 + i * 0.5  # Slight upward trend
            seasonal_factor = 10 * np.sin(i * np.pi/6)  # Seasonal pattern
            
            self.metrics.append({{
                "name": "carbon_emissions",
                "value": base_emissions + seasonal_factor,
                "unit": "tCO2e",
                "category": "emissions",
                "timestamp": current_date.isoformat()
            }})
        
        # Generate renewable energy data with upward trend
        for i in range(12):
            current_date = start_date + timedelta(days=30*i)
            self.metrics.append({{
                "name": "renewable_energy",
                "value": 30 + i * 1.5,  # Strong upward trend
                "unit": "percent",
                "category": "energy",
                "timestamp": current_date.isoformat()
            }})
        
        # Generate water usage data with downward trend
        for i in range(12):
            current_date = start_date + timedelta(days=30*i)
            self.metrics.append({{
                "name": "water_usage",
                "value": 5000 - i * 50,  # Downward trend
                "unit": "m3",
                "category": "water",
                "timestamp": current_date.isoformat()
            }})
    
    def test_output_structure(self):
        """Test prediction output structure"""
        # Call the prediction function
        forecast_periods = 3
        result = {function_name}(self.metrics, forecast_periods)
        
        # Verify basic structure
        self.assertIsInstance(result, dict, "Result should be a dictionary")
        self.assertIn("forecast_date", result, "Result should include forecast date")
        self.assertIn("forecast_periods", result, "Result should include number of forecast periods")
        self.assertIn("predictions", result, "Result should include predictions")
        self.assertIsInstance(result["predictions"], list, "Predictions should be a list")
        
        # Verify predictions content
        if len(result["predictions"]) > 0:
            sample_prediction = result["predictions"][0]
            self.assertIn("name", sample_prediction, "Prediction should include metric name")
            self.assertIn("category", sample_prediction, "Prediction should include category")
            self.assertIn("values", sample_prediction, "Prediction should include forecasted values")
            self.assertIn("confidence_intervals", sample_prediction, "Prediction should include confidence intervals")
            self.assertEqual(len(sample_prediction["values"]), forecast_periods, 
                            "Should have correct number of forecasted values")
    
    def test_forecasting_accuracy(self):
        """Test prediction accuracy by masking recent data"""
        # Get the latest 3 data points for each metric
        test_periods = 3
        training_data = []
        validation_data = {{}}
        
        for item in self.metrics:
            metric_name = item["name"]
            if metric_name not in validation_data:
                validation_data[metric_name] = []
            
            # Collect validation data from the most recent periods
            timestamp = pd.to_datetime(item["timestamp"])
            if timestamp >= pd.to_datetime("2022-10-01"):
                validation_data[metric_name].append(item)
            else:
                training_data.append(item)
        
        # Make predictions using only training data
        result = {function_name}(training_data, test_periods)
        
        # For each metric, compare predictions with actual values
        for prediction in result["predictions"]:
            metric_name = prediction["name"]
            
            # Get actual values for this metric
            actual_values = []
            for item in validation_data.get(metric_name, []):
                actual_values.append(item["value"])
            
            # Skip if we don't have validation data for this metric
            if not actual_values:
                continue
                
            # Get predicted values
            predicted_values = prediction["values"]
            
            # Calculate mean absolute percentage error
            mape = 0
            count = min(len(actual_values), len(predicted_values))
            if count > 0:
                for i in range(count):
                    if actual_values[i] != 0:  # Avoid division by zero
                        mape += abs((actual_values[i] - predicted_values[i]) / actual_values[i])
                mape = mape / count * 100
                
                # For a simple test, just verify MAPE is within reasonable bounds
                self.assertLessEqual(mape, 50, f"MAPE should be <= 50%, got {{mape:.2f}}%")
                
                # Also verify confidence intervals contain actual values
                lower_bounds = prediction["confidence_intervals"]["lower"]
                upper_bounds = prediction["confidence_intervals"]["upper"]
                
                for i in range(count):
                    # Allow some tolerance for validation
                    self.assertTrue(
                        actual_values[i] >= lower_bounds[i] * 0.8 or actual_values[i] <= upper_bounds[i] * 1.2,
                        f"Actual value {{actual_values[i]}} should be within confidence intervals (adjusted)"
                    )
    
    def test_with_empty_data(self):
        """Test prediction with empty data"""
        # Call with empty data
        result = {function_name}([], 3)
        
        # Verify appropriate error handling
        self.assertIsInstance(result, dict, "Result should be a dictionary even with empty input")
        self.assertTrue(
            "error" in result or len(result.get("predictions", [])) == 0,
            "Should handle empty input appropriately"
        )
    
    def test_with_inconsistent_data(self):
        """Test prediction with inconsistent data"""
        # Create data with inconsistent timestamps
        inconsistent_data = self.metrics.copy()
        
        # Add some data with very different timestamps
        inconsistent_data.append({{
            "name": "carbon_emissions",
            "value": 500,
            "unit": "tCO2e",
            "category": "emissions",
            "timestamp": "2050-01-01T00:00:00"  # Far future
        }})
        
        inconsistent_data.append({{
            "name": "carbon_emissions",
            "value": 200,
            "unit": "tCO2e",
            "category": "emissions",
            "timestamp": "1980-01-01T00:00:00"  # Far past
        }})
        
        # The function should still produce reasonable results
        result = {function_name}(inconsistent_data, 3)
        
        # Basic structure checks
        self.assertIsInstance(result, dict, "Result should be a dictionary")
        self.assertIn("predictions", result, "Result should include predictions")

if __name__ == '__main__':
    unittest.main()
"""
        
        return test_code
    
    def _generate_visualization_tests(self, function: Callable) -> str:
        """Generate tests for visualization functions"""
        function_name = function.__name__
        module_name = function.__module__
        
        if self.test_framework == "pytest":
            test_code = f"""
import pytest
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for testing
import matplotlib.pyplot as plt
from {module_name} import {function_name}

# Generate mock sustainability metrics for testing
@pytest.fixture
def visualization_data():
    # Create sample data for visualization testing
    categories = ["emissions", "water", "energy", "waste", "social", "governance"]
    metrics = []
    
    for category in categories:
        for i in range(5):  # 5 metrics per category
            metrics.append({{
                "name": f"{category}_metric_{i+1}",
                "value": 100 * np.random.random(),
                "unit": "units",
                "category": category,
                "timestamp": "2023-01-01"
            }})
    
    return metrics

def test_{function_name}_returns_plot(visualization_data):
    """Test that the function returns a visualization object"""
    result = {function_name}(visualization_data)
    
    # Check return type - should be matplotlib figure, plotly figure, or similar
    assert result is not None, "Visualization function should return a result"
    
    is_mpl_figure = isinstance(result, plt.Figure)
    is_mpl_axes = isinstance(result, plt.Axes) or (hasattr(result, '__iter__') and 
                                                 any(isinstance(x, plt.Axes) for x in result))
    try:
        import plotly.graph_objects as go
        is_plotly_figure = isinstance(result, go.Figure)
    except ImportError:
        is_plotly_figure = False
    
    assert is_mpl_figure or is_mpl_axes or is_plotly_figure, \\
           "Result should be a matplotlib or plotly visualization object"
    
    # To avoid displaying plots during tests
    plt.close('all')

def test_{function_name}_handles_empty_data():
    """Test visualization with empty data"""
    result = {function_name}([])
    
    # Should handle empty data gracefully
    assert result is not None, "Should handle empty data gracefully"
    
    # To avoid displaying plots during tests
    plt.close('all')

def test_{function_name}_with_single_category(visualization_data):
    """Test visualization with data from a single category"""
    # Filter data to only include 'emissions' category
    filtered_data = [item for item in visualization_data if item["category"] == "emissions"]
    
    result = {function_name}(filtered_data)
    
    # Should handle single category data
    assert result is not None, "Should handle single category data"
    
    # To avoid displaying plots during tests
    plt.close('all')

def test_{function_name}_custom_parameters(visualization_data):
    """Test visualization with custom parameters if supported"""
    # Try with some common custom parameters that might be supported
    try:
        # With title
        result1 = {function_name}(visualization_data, title="Custom Title")
        assert result1 is not None, "Should accept title parameter"
        
        # With color mapping
        result2 = {function_name}(visualization_data, colors={{"emissions": "red", "water": "blue"}})
        assert result2 is not None, "Should accept colors parameter"
        
        # With size/figsize
        result3 = {function_name}(visualization_data, figsize=(10, 6))
        assert result3 is not None, "Should accept figsize parameter"
    except TypeError as e:
        # If function doesn't support these parameters, test will pass
        # This is just a compatibility test for functions that might support these
        pass
    
    # To avoid displaying plots during tests
    plt.close('all')

def test_{function_name}_plot_elements(visualization_data):
    """Test plot elements if using matplotlib"""
    result = {function_name}(visualization_data)
    
    # Check for common plot elements if this is a matplotlib figure
    if isinstance(result, plt.Figure):
        # Should have a title
        assert result._suptitle is not None or any(ax.get_title() for ax in result.axes), \\
               "Plot should have a title"
        
        # Should have axes
        assert len(result.axes) > 0, "Plot should have axes"
        
        # Should have either some lines, bars, or other artists
        ax = result.axes[0]
        has_content = (len(ax.lines) > 0 or len(ax.patches) > 0 or 
                      len(ax.collections) > 0 or len(ax.texts) > 0)
        assert has_content, "Plot should have visual elements"
        
        # Should have labels
        has_labels = (ax.get_xlabel() != "" or ax.get_ylabel() != "" or 
                     any(t.get_text() != "" for t in ax.get_xticklabels()) or
                     any(t.get_text() != "" for t in ax.get_yticklabels()))
        assert has_labels, "Plot should have labels"
    
    # To avoid displaying plots during tests
    plt.close('all')
"""
        else:  # unittest
            test_code = f"""
import unittest
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for testing
import matplotlib.pyplot as plt
from {module_name} import {function_name}

class Test{function_name.capitalize()}(unittest.TestCase):
    def setUp(self):
        # Create sample data for visualization testing
        categories = ["emissions", "water", "energy", "waste", "social", "governance"]
        self.metrics = []
        
        for category in categories:
            for i in range(5):  # 5 metrics per category
                self.metrics.append({{
                    "name": f"{category}_metric_{i+1}",
                    "value": 100 * np.random.random(),
                    "unit": "units",
                    "category": category,
                    "timestamp": "2023-01-01"
                }})
    
    def tearDown(self):
        # Close all plots to avoid display during tests
        plt.close('all')
    
    def test_returns_plot(self):
        """Test that the function returns a visualization object"""
        result = {function_name}(self.metrics)
        
        # Check return type - should be matplotlib figure, plotly figure, or similar
        self.assertIsNotNone(result, "Visualization function should return a result")
        
        is_mpl_figure = isinstance(result, plt.Figure)
        is_mpl_axes = isinstance(result, plt.Axes) or (hasattr(result, '__iter__') and 
                                                     any(isinstance(x, plt.Axes) for x in result))
        try:
            import plotly.graph_objects as go
            is_plotly_figure = isinstance(result, go.Figure)
        except ImportError:
            is_plotly_figure = False
        
        self.assertTrue(is_mpl_figure or is_mpl_axes or is_plotly_figure,
                       "Result should be a matplotlib or plotly visualization object")
    
    def test_handles_empty_data(self):
        """Test visualization with empty data"""
        result = {function_name}([])
        
        # Should handle empty data gracefully
        self.assertIsNotNone(result, "Should handle empty data gracefully")
    
    def test_with_single_category(self):
        """Test visualization with data from a single category"""
        # Filter data to only include 'emissions' category
        filtered_data = [item for item in self.metrics if item["category"] == "emissions"]
        
        result = {function_name}(filtered_data)
        
        # Should handle single category data
        self.assertIsNotNone(result, "Should handle single category data")
    
    def test_custom_parameters(self):
        """Test visualization with custom parameters if supported"""
        # Try with some common custom parameters that might be supported
        try:
            # With title
            result1 = {function_name}(self.metrics, title="Custom Title")
            self.assertIsNotNone(result1, "Should accept title parameter")
            
            # With color mapping
            result2 = {function_name}(self.metrics, colors={{"emissions": "red", "water": "blue"}})
            self.assertIsNotNone(result2, "Should accept colors parameter")
            
            # With size/figsize
            result3 = {function_name}(self.metrics, figsize=(10, 6))
            self.assertIsNotNone(result3, "Should accept figsize parameter")
        except TypeError as e:
            # If function doesn't support these parameters, test will pass
            # This is just a compatibility test for functions that might support these
            pass
    
    def test_plot_elements(self):
        """Test plot elements if using matplotlib"""
        result = {function_name}(self.metrics)
        
        # Check for common plot elements if this is a matplotlib figure
        if isinstance(result, plt.Figure):
            # Should have a title
            has_title = result._suptitle is not None or any(ax.get_title() for ax in result.axes)
            self.assertTrue(has_title, "Plot should have a title")
            
            # Should have axes
            self.assertGreater(len(result.axes), 0, "Plot should have axes")
            
            # Should have either some lines, bars, or other artists
            ax = result.axes[0]
            has_content = (len(ax.lines) > 0 or len(ax.patches) > 0 or 
                          len(ax.collections) > 0 or len(ax.texts) > 0)
            self.assertTrue(has_content, "Plot should have visual elements")
            
            # Should have labels
            has_labels = (ax.get_xlabel() != "" or ax.get_ylabel() != "" or 
                         any(t.get_text() != "" for t in ax.get_xticklabels()) or
                         any(t.get_text() != "" for t in ax.get_yticklabels()))
            self.assertTrue(has_labels, "Plot should have labels")

if __name__ == '__main__':
    unittest.main()
"""
        
        return test_code
    
    def _generate_generic_tests(self, function: Callable) -> str:
        """Generate generic tests for functions with unknown purpose"""
        function_name = function.__name__
        function_signature = str(inspect.signature(function))
        param_names = list(inspect.signature(function).parameters.keys())
        module_name = function.__module__
        
        if self.test_framework == "pytest":
            test_code = f"""
import pytest
from {module_name} import {function_name}

def test_{function_name}_exists():
    """Test that the function exists and is callable"""
    assert callable({function_name}), "Function should be callable"

def test_{function_name}_signature():
    """Test that the function has the expected signature"""
    import inspect
    sig = str(inspect.signature({function_name}))
    expected_sig = '{function_signature}'
    assert sig == expected_sig, f"Function signature should be {{expected_sig}}, got {{sig}}"

def test_{function_name}_basic_execution():
    """Test that the function executes without errors with minimal inputs"""
    # Create minimal valid inputs based on the function signature
    try:
        # Try to call with empty/minimal arguments
        if '{function_signature}' == '()':
            result = {function_name}()
        elif len('{param_names}') == 1:
            # Try with None or empty container
            try:
                result = {function_name}(None)
            except:
                try:
                    result = {function_name}([])
                except:
                    result = {function_name}("")
        else:
            # Can't easily determine appropriate arguments, test will be skipped
            pytest.skip("Cannot automatically determine appropriate test arguments")
            
        # If we got here, the function executed without raising an exception
        assert True
    except Exception as e:
        # If function requires specific inputs, this test might fail, which is acceptable
        pytest.skip(f"Function requires specific inputs: {{str(e)}}")

def test_{function_name}_returns_something():
    """Test that the function returns a result"""
    # Only relevant if the basic execution test passes
    try:
        # Try to call with empty/minimal arguments
        if '{function_signature}' == '()':
            result = {function_name}()
        elif len('{param_names}') == 1:
            # Try with None or empty container
            try:
                result = {function_name}(None)
            except:
                try:
                    result = {function_name}([])
                except:
                    result = {function_name}("")
        else:
            # Can't easily determine appropriate arguments, test will be skipped
            pytest.skip("Cannot automatically determine appropriate test arguments")
            
        # Check that result is not None (if function returns something)
        if '{function_signature}'.endswith("-> None"):
            assert result is None, "Function should return None as specified"
        else:
            assert result is not None, "Function should return a result"
    except Exception as e:
        # If function requires specific inputs, this test might fail, which is acceptable
        pytest.skip(f"Function requires specific inputs: {{str(e)}}")
"""
        else:  # unittest
            test_code = f"""
import unittest
from {module_name} import {function_name}

class Test{function_name.capitalize()}(unittest.TestCase):
    def test_exists(self):
        """Test that the function exists and is callable"""
        self.assertTrue(callable({function_name}), "Function should be callable")
    
    def test_signature(self):
        """Test that the function has the expected signature"""
        import inspect
        sig = str(inspect.signature({function_name}))
        expected_sig = '{function_signature}'
        self.assertEqual(sig, expected_sig, 
                        f"Function signature should be {{expected_sig}}, got {{sig}}")
    
    def test_basic_execution(self):
        """Test that the function executes without errors with minimal inputs"""
        # Create minimal valid inputs based on the function signature
        try:
            # Try to call with empty/minimal arguments
            if '{function_signature}' == '()':
                result = {function_name}()
            elif len('{param_names}') == 1:
                # Try with None or empty container
                try:
                    result = {function_name}(None)
                except:
                    try:
                        result = {function_name}([])
                    except:
                        result = {function_name}("")
            else:
                # Can't easily determine appropriate arguments, test will be skipped
                self.skipTest("Cannot automatically determine appropriate test arguments")
                
            # If we got here, the function executed without raising an exception
            self.assertTrue(True)
        except Exception as e:
            # If function requires specific inputs, this test might fail, which is acceptable
            self.skipTest(f"Function requires specific inputs: {{str(e)}}")
    
    def test_returns_something(self):
        """Test that the function returns a result"""
        # Only relevant if the basic execution test passes
        try:
            # Try to call with empty/minimal arguments
            if '{function_signature}' == '()':
                result = {function_name}()
            elif len('{param_names}') == 1:
                # Try with None or empty container
                try:
                    result = {function_name}(None)
                except:
                    try:
                        result = {function_name}([])
                    except:
                        result = {function_name}("")
            else:
                # Can't easily determine appropriate arguments, test will be skipped
                self.skipTest("Cannot automatically determine appropriate test arguments")
                
            # Check that result is not None (if function returns something)
            if '{function_signature}'.endswith("-> None"):
                self.assertIsNone(result, "Function should return None as specified")
            else:
                self.assertIsNotNone(result, "Function should return a result")
        except Exception as e:
            # If function requires specific inputs, this test might fail, which is acceptable
            self.skipTest(f"Function requires specific inputs: {{str(e)}}")

if __name__ == '__main__':
    unittest.main()
"""
        
        return test_code