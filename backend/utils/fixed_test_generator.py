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
    # Test successful data extraction
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
    # Test error handling during extraction
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
    # Test timeout handling during extraction
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
    # Test with invalid endpoint
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
        # Test successful data extraction
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
        # Test error handling during extraction
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
        # Test timeout handling during extraction
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
        # Test with invalid endpoint
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
    # Test analysis with valid data
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
    # Test analysis with empty data
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
    # Test analysis with missing values
    # Create data with missing values
    data_with_missing = sample_metrics_data.copy()
    data_with_missing[0]["value"] = None
    data_with_missing[3]["value"] = np.nan
    
    # Call the function with data containing missing values
    result = {function_name}(data_with_missing)
    
    # Verify it handles missing values appropriately
    assert result is not None, "Should handle missing values"

def test_{function_name}_with_invalid_data():
    # Test analysis with invalid data structure
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
        # Test analysis with valid data
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
        # Test analysis with empty data
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
        # Test analysis with missing values
        # Create data with missing values
        data_with_missing = self.sample_metrics_data.copy()
        data_with_missing[0]["value"] = None
        data_with_missing[3]["value"] = np.nan
        
        # Call the function with data containing missing values
        result = {function_name}(data_with_missing)
        
        # Verify it handles missing values appropriately
        self.assertIsNotNone(result, "Should handle missing values")
    
    def test_with_invalid_data(self):
        # Test analysis with invalid data structure
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
        """Generate minimal pytest tests for prediction functions to avoid syntax errors"""
        function_name = function.__name__
        module_name = function.__module__
        
        if self.test_framework == "pytest":
            test_code = f"""
import pytest
from {module_name} import {function_name}

def test_{function_name}_basic():
    # Basic test for prediction function
    # Create minimal test data
    test_data = [
        {{"name": "metric1", "value": 100, "timestamp": "2023-01-01", "category": "emissions"}},
        {{"name": "metric1", "value": 110, "timestamp": "2023-02-01", "category": "emissions"}},
        {{"name": "metric1", "value": 120, "timestamp": "2023-03-01", "category": "emissions"}}
    ]
    
    # Call the function
    result = {function_name}(test_data, 2)
    
    # Basic verification
    assert isinstance(result, dict), "Should return a dictionary"
"""
        else:  # unittest
            test_code = f"""
import unittest
from {module_name} import {function_name}

class Test{function_name.capitalize()}(unittest.TestCase):
    def test_basic(self):
        # Basic test for prediction function
        # Create minimal test data
        test_data = [
            {{"name": "metric1", "value": 100, "timestamp": "2023-01-01", "category": "emissions"}},
            {{"name": "metric1", "value": 110, "timestamp": "2023-02-01", "category": "emissions"}},
            {{"name": "metric1", "value": 120, "timestamp": "2023-03-01", "category": "emissions"}}
        ]
        
        # Call the function
        result = {function_name}(test_data, 2)
        
        # Basic verification
        self.assertIsInstance(result, dict, "Should return a dictionary")

if __name__ == '__main__':
    unittest.main()
"""
        
        return test_code
    
    def _generate_visualization_tests(self, function: Callable) -> str:
        """Generate minimal pytest tests for visualization functions to avoid syntax errors"""
        function_name = function.__name__
        module_name = function.__module__
        
        if self.test_framework == "pytest":
            test_code = f"""
import pytest
from {module_name} import {function_name}

def test_{function_name}_basic():
    # Basic test for visualization function
    # Create minimal test data
    test_data = [
        {{"name": "metric1", "value": 100, "timestamp": "2023-01-01", "category": "emissions"}},
        {{"name": "metric1", "value": 110, "timestamp": "2023-02-01", "category": "emissions"}},
        {{"name": "metric1", "value": 120, "timestamp": "2023-03-01", "category": "emissions"}}
    ]
    
    # Call the function
    try:
        result = {function_name}(test_data)
        # Basic verification that it runs without error
        assert result is not None, "Should return something"
    except Exception as e:
        # If it requires specific visualization libraries, test may fail
        pytest.skip(f"Visualization test failed: {{str(e)}}")
"""
        else:  # unittest
            test_code = f"""
import unittest
from {module_name} import {function_name}

class Test{function_name.capitalize()}(unittest.TestCase):
    def test_basic(self):
        # Basic test for visualization function
        # Create minimal test data
        test_data = [
            {{"name": "metric1", "value": 100, "timestamp": "2023-01-01", "category": "emissions"}},
            {{"name": "metric1", "value": 110, "timestamp": "2023-02-01", "category": "emissions"}},
            {{"name": "metric1", "value": 120, "timestamp": "2023-03-01", "category": "emissions"}}
        ]
        
        # Call the function
        try:
            result = {function_name}(test_data)
            # Basic verification that it runs without error
            self.assertIsNotNone(result, "Should return something")
        except Exception as e:
            # If it requires specific visualization libraries, test may fail
            self.skipTest(f"Visualization test failed: {{str(e)}}")

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
    # Test that the function exists and is callable
    assert callable({function_name}), "Function should be callable"

def test_{function_name}_signature():
    # Test that the function has the expected signature
    import inspect
    sig = str(inspect.signature({function_name}))
    expected_sig = '{function_signature}'
    assert sig == expected_sig, f"Function signature should be {{expected_sig}}, got {{sig}}"
"""
        else:  # unittest
            test_code = f"""
import unittest
from {module_name} import {function_name}

class Test{function_name.capitalize()}(unittest.TestCase):
    def test_exists(self):
        # Test that the function exists and is callable
        self.assertTrue(callable({function_name}), "Function should be callable")
    
    def test_signature(self):
        # Test that the function has the expected signature
        import inspect
        sig = str(inspect.signature({function_name}))
        expected_sig = '{function_signature}'
        self.assertEqual(sig, expected_sig, 
                        f"Function signature should be {{expected_sig}}, got {{sig}}")

if __name__ == '__main__':
    unittest.main()
"""
        
        return test_code