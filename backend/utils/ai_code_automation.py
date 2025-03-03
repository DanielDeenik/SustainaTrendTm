"""
AI-Powered Development Automation Module

This module provides utilities for AI-driven code generation, optimization, 
and testing for the SustainaTrend™ platform.

Key capabilities:
1. Code completion & refactoring
2. Automated unit test generation
3. Performance optimization
4. Sustainability data extraction
"""
import os
import re
import logging
import inspect
import json
import time
import random
from typing import Callable, Dict, List, Any, Optional, Union
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import AI libraries (with proper fallbacks)
try:
    import openai
    from langchain.chat_models import ChatOpenAI
    from langchain.chains import LLMChain
    AI_LIBRARIES_AVAILABLE = True
    logger.info("AI libraries loaded successfully")
except ImportError:
    AI_LIBRARIES_AVAILABLE = False
    logger.warning("AI libraries not available for code automation. Using fallback mechanisms.")

def optimize_function(
    function: Callable,
    optimization_goal: str = "efficiency",
    context: str = "sustainability"
) -> str:
    """
    Use AI to optimize a function's code based on the specified goal.
    
    Args:
        function: The function to optimize
        optimization_goal: What to optimize for (efficiency, readability, etc.)
        context: Domain context for optimization
        
    Returns:
        Optimized function code as a string
    """
    function_name = function.__name__
    function_code = inspect.getsource(function)
    
    logger.info(f"Optimizing function '{function_name}' for {optimization_goal}")
    
    if AI_LIBRARIES_AVAILABLE and os.getenv('OPENAI_API_KEY'):
        try:
            # Use OpenAI for optimization
            completion = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": f"You are an expert Python developer specializing in {context} applications. Optimize the following function for {optimization_goal}."},
                    {"role": "user", "content": f"Please optimize this function:\n\n{function_code}\n\nFocus on {optimization_goal} while maintaining functionality. Provide only the optimized code with no explanation."}
                ],
                temperature=0.3,
                max_tokens=1500
            )
            optimized_code = completion.choices[0].message.content.strip()
            return optimized_code
        except Exception as e:
            logger.error(f"Error using OpenAI for function optimization: {str(e)}")
            # Fall back to mock optimization
    
    # If AI isn't available or fails, use a mock optimization
    return _generate_mock_optimized_function(function, optimization_goal, context)

def generate_unit_tests(
    function: Callable,
    test_framework: str = "pytest",
    test_coverage: float = 0.8
) -> str:
    """
    Generate unit tests for a given function using AI.
    
    Args:
        function: The function to generate tests for
        test_framework: Testing framework to use (pytest, unittest)
        test_coverage: Target test coverage (0.0-1.0)
        
    Returns:
        Unit test code as a string
    """
    function_name = function.__name__
    function_code = inspect.getsource(function)
    
    logger.info(f"Generating tests for function '{function_name}' using {test_framework}")
    
    if AI_LIBRARIES_AVAILABLE and os.getenv('OPENAI_API_KEY'):
        try:
            # Use OpenAI for test generation
            completion = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": f"You are an expert Python tester who creates comprehensive test cases for sustainability-related code."},
                    {"role": "user", "content": f"Generate {test_framework} tests for this function:\n\n{function_code}\n\nCreate tests that achieve at least {test_coverage*100}% coverage. Include tests for edge cases, error handling, and normal operation. Provide only the test code with no explanation."}
                ],
                temperature=0.3,
                max_tokens=1500
            )
            test_code = completion.choices[0].message.content.strip()
            return test_code
        except Exception as e:
            logger.error(f"Error using OpenAI for test generation: {str(e)}")
            # Fall back to mock test generation
    
    # If AI isn't available or fails, use built-in generators
    return generate_mock_unit_tests(function, test_framework)

def generate_mock_unit_tests(function: Callable, test_framework: str = "pytest") -> str:
    """Generate mock unit tests when AI is not available"""
    function_name = function.__name__
    module_name = function.__module__ if function.__module__ != "__main__" else "main"
    params = list(inspect.signature(function).parameters.keys())
    
    if test_framework == "pytest":
        return f"""
import pytest
from {module_name} import {function_name}

def test_{function_name}_basic():
    \"\"\"Basic test for {function_name}\"\"\"
    # TODO: Replace with appropriate test values
    {'result = ' + function_name + '(' + ', '.join(['None' for _ in params]) + ')' if params else 'result = ' + function_name + '()'}
    assert result is not None

def test_{function_name}_edge_cases():
    \"\"\"Test edge cases for {function_name}\"\"\"
    # TODO: Implement edge case tests
    pass

def test_{function_name}_error_handling():
    \"\"\"Test error handling in {function_name}\"\"\"
    # TODO: Implement error handling tests
    pass
"""
    else:  # unittest
        return f"""
import unittest
from {module_name} import {function_name}

class Test{function_name.capitalize()}(unittest.TestCase):
    def test_basic(self):
        \"\"\"Basic test for {function_name}\"\"\"
        # TODO: Replace with appropriate test values
        {'result = ' + function_name + '(' + ', '.join(['None' for _ in params]) + ')' if params else 'result = ' + function_name + '()'}
        self.assertIsNotNone(result)
    
    def test_edge_cases(self):
        \"\"\"Test edge cases for {function_name}\"\"\"
        # TODO: Implement edge case tests
        pass
    
    def test_error_handling(self):
        \"\"\"Test error handling in {function_name}\"\"\"
        # TODO: Implement error handling tests
        pass

if __name__ == '__main__':
    unittest.main()
"""

def extract_sustainability_data(api_endpoint: str, data_format: str = "json") -> Dict[str, Any]:
    """
    Extract sustainability data from an API endpoint with error handling and validation.
    
    Args:
        api_endpoint: The URL of the API endpoint to extract data from
        data_format: Format of the data (json, csv, xml)
        
    Returns:
        Dict containing extracted sustainability data
    """
    import requests
    
    logger.info(f"Extracting sustainability data from: {api_endpoint}")
    
    result = {
        "metadata": {
            "timestamp": datetime.now().isoformat(),
            "source": api_endpoint,
            "status": "pending"
        },
        "metrics": []
    }
    
    try:
        # Make the API request with timeout
        response = requests.get(api_endpoint, timeout=10)
        
        # Check if the request was successful
        if response.status_code == 200:
            result["metadata"]["status"] = "success"
            
            if data_format == "json":
                data = response.json()
                
                # Extract metrics from JSON data
                if "data" in data and isinstance(data["data"], dict):
                    # Handle nested data structure
                    metrics = []
                    extract_sustainability_metrics(data["data"], metrics=metrics)
                    result["metrics"] = metrics
                elif "data" in data and isinstance(data["data"], list):
                    # Handle flat data structure
                    result["metrics"] = data["data"]
                else:
                    # Handle unknown data structure
                    result["metadata"]["status"] = "partial"
                    result["metadata"]["warning"] = "Unknown data structure"
                    result["metrics"] = []
            
            elif data_format == "csv":
                # TODO: Implement CSV parsing
                pass
            
            elif data_format == "xml":
                # TODO: Implement XML parsing
                pass
            
            else:
                result["metadata"]["status"] = "failed"
                result["metadata"]["error"] = f"Unsupported data format: {data_format}"
        
        else:
            # Handle failed request
            result["metadata"]["status"] = "failed"
            result["metadata"]["error"] = f"API request failed with status code: {response.status_code}"
            
    except requests.exceptions.Timeout:
        # Handle timeout
        result["metadata"]["status"] = "failed"
        result["metadata"]["error"] = "Request timed out"
    
    except requests.exceptions.RequestException as e:
        # Handle other request exceptions
        result["metadata"]["status"] = "failed"
        result["metadata"]["error"] = f"Request failed: {str(e)}"
    
    except Exception as e:
        # Handle any other exceptions
        result["metadata"]["status"] = "failed"
        result["metadata"]["error"] = f"Error processing data: {str(e)}"
    
    return result

def extract_sustainability_metrics(data_obj, current_path="", metrics=None):
    """
    Recursively extract sustainability metrics from nested data structures.
    
    Args:
        data_obj: Data object to extract metrics from
        current_path: Current path in the data structure
        metrics: List to store extracted metrics
        
    Returns:
        None (metrics are added to the metrics list)
    """
    if metrics is None:
        metrics = []
    
    # If it's a dictionary
    if isinstance(data_obj, dict):
        # Check if it looks like a metric
        if all(key in data_obj for key in ["name", "value"]) and "name" in data_obj:
            metrics.append(data_obj)
        else:
            # Recursively process each item
            for key, value in data_obj.items():
                new_path = f"{current_path}.{key}" if current_path else key
                extract_sustainability_metrics(value, new_path, metrics)
    
    # If it's a list
    elif isinstance(data_obj, list):
        for i, item in enumerate(data_obj):
            new_path = f"{current_path}[{i}]"
            extract_sustainability_metrics(item, new_path, metrics)

def suggest_code_improvements(
    code: str, 
    improvement_type: str = "all"
) -> List[Dict[str, str]]:
    """
    Analyze code and suggest improvements for sustainability data processing.
    
    Args:
        code: The source code to analyze
        improvement_type: Type of improvements to suggest (performance, security, etc.)
        
    Returns:
        List of improvement suggestions with explanations
    """
    logger.info(f"Analyzing code for {improvement_type} improvements")
    
    if AI_LIBRARIES_AVAILABLE and os.getenv('OPENAI_API_KEY'):
        try:
            # Use OpenAI for code improvement suggestions
            completion = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": f"You are an expert Python code reviewer specializing in sustainability data processing."},
                    {"role": "user", "content": f"Analyze this code and suggest {improvement_type} improvements:\n\n{code}\n\nProvide suggestions in a structured format with 'suggestion', 'issue', and 'explanation' fields. Focus on {improvement_type} improvements."}
                ],
                temperature=0.3,
                max_tokens=1500
            )
            
            # Parse the response to extract suggestions
            response_text = completion.choices[0].message.content
            
            # Extract suggestions from the text
            # This is a simplified parser and may need to be improved
            suggestions = []
            current_suggestion = {}
            
            for line in response_text.split('\n'):
                line = line.strip()
                
                if line.startswith('Suggestion:') or line.startswith('Improvement:'):
                    if current_suggestion and 'suggestion' in current_suggestion:
                        suggestions.append(current_suggestion)
                    current_suggestion = {'suggestion': line.split(':', 1)[1].strip()}
                
                elif line.startswith('Issue:'):
                    if 'suggestion' in current_suggestion:
                        current_suggestion['issue'] = line.split(':', 1)[1].strip()
                
                elif line.startswith('Explanation:'):
                    if 'suggestion' in current_suggestion:
                        current_suggestion['explanation'] = line.split(':', 1)[1].strip()
            
            # Add the last suggestion
            if current_suggestion and 'suggestion' in current_suggestion:
                suggestions.append(current_suggestion)
            
            # Ensure all suggestions have the required fields
            for suggestion in suggestions:
                if 'issue' not in suggestion:
                    suggestion['issue'] = "Code could be improved"
                if 'explanation' not in suggestion:
                    suggestion['explanation'] = "See suggestion details"
            
            return suggestions
        
        except Exception as e:
            logger.error(f"Error using OpenAI for code suggestions: {str(e)}")
            # Fall back to mock suggestions
    
    # If AI isn't available or fails, use mock suggestions
    return generate_mock_code_suggestions(code, improvement_type)

def generate_mock_code_suggestions(code: str, improvement_type: str = "all") -> List[Dict[str, str]]:
    """Generate mock code improvement suggestions when AI is not available"""
    logger.info("Generating mock code improvement suggestions")
    
    # Identify common issues in the code
    suggestions = []
    
    # Check for raw string iteration (performance)
    if "for i in range(len(" in code:
        suggestions.append({
            "suggestion": "Use direct iteration over collections",
            "issue": "Inefficient iteration using range(len())",
            "explanation": "Instead of 'for i in range(len(data))', use 'for item in data' for better readability and performance."
        })
    
    # Check for print statements (production readiness)
    if re.search(r"\bprint\(", code):
        suggestions.append({
            "suggestion": "Replace print statements with proper logging",
            "issue": "Use of print statements",
            "explanation": "Replace print statements with proper logging (e.g., logging.info()) for better production readiness."
        })
    
    # Check for hard-coded values (maintainability)
    if re.search(r"=\s*['\"][\w\s./]+['\"]", code) or re.search(r"=\s*\d+\.\d+", code):
        suggestions.append({
            "suggestion": "Extract magic numbers and strings as constants",
            "issue": "Hard-coded values in the code",
            "explanation": "Define constants at the top of the module for better maintainability and documentation."
        })
    
    # Check for missing error handling (robustness)
    if "except:" in code and not re.search(r"except\s+\w+", code):
        suggestions.append({
            "suggestion": "Use specific exception handling",
            "issue": "Bare 'except:' clause",
            "explanation": "Catch specific exceptions rather than using a bare 'except:' clause, which can hide bugs."
        })
    
    # Check for sustainability-specific improvements
    if improvement_type == "sustainability" or improvement_type == "all":
        suggestions.append({
            "suggestion": "Add sustainability metadata to results",
            "issue": "Missing sustainability context",
            "explanation": "Include metadata about the sustainability context (e.g., emissions category, compliance framework) in the function results."
        })
    
    # If we couldn't find specific issues, add a generic suggestion
    if not suggestions:
        suggestions.append({
            "suggestion": "Add comprehensive documentation",
            "issue": "Documentation could be improved",
            "explanation": "Add more detailed docstrings explaining the sustainability context and expected data formats."
        })
    
    return suggestions

def _generate_mock_optimized_function(function: Callable, optimization_goal: str, context: str) -> str:
    """Generate a mock optimized version of a function when AI is not available"""
    function_code = inspect.getsource(function)
    
    # Simple optimizations based on common patterns
    optimized_code = function_code
    
    # Add imports
    import_section = """import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)
"""
    
    # Add retry functionality for data extraction functions
    if "extract" in function.__name__ or "get" in function.__name__ or "fetch" in function.__name__:
        optimized_code = re.sub(
            r"(def\s+\w+\s*\([^)]*\)\s*:.*?)(\s+import requests)",
            r"\1\n    from requests.adapters import HTTPAdapter\n    from urllib3.util.retry import Retry\n\2",
            optimized_code
        )
        
        optimized_code = re.sub(
            r"(response\s*=\s*requests\.get\([^)]+\))",
            r"""    # Setup retry strategy
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session = requests.Session()
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    # Log request attempt
    logger.info(f"Requesting data from {api_endpoint}")
    
    # Make request with retry strategy
    response = session.get(api_endpoint, timeout=10)""",
            optimized_code
        )
    
    # Add caching for analysis functions
    if "analyze" in function.__name__ or "calculate" in function.__name__ or "compute" in function.__name__:
        optimized_code = re.sub(
            r"(def\s+\w+\s*\([^)]*\)\s*:)",
            r"from functools import lru_cache\n\n@lru_cache(maxsize=32)\n\1",
            optimized_code
        )
    
    # Add validation for all functions
    if "data" in inspect.signature(function).parameters:
        optimized_code = re.sub(
            r"(def\s+\w+\s*\([^)]*\)\s*:.*?)(\s+if (?:not )?(?:\w+))",
            r"""\1
    # Validate input data
    if data is None:
        logger.warning("Input data is None")
        return {"error": "Input data is None", "status": "failed"}
        
    if not isinstance(data, list):
        logger.warning(f"Expected list, got {type(data).__name__}")
        return {"error": f"Expected list, got {type(data).__name__}", "status": "failed"}
        
    if len(data) == 0:
        logger.info("Input data is empty")
\2""",
            optimized_code
        )
    
    # Add comprehensive error handling
    optimized_code = re.sub(
        r"(except [^:]+:)",
        r"\1\n        logger.error(f\"Error: {str(e)}\")",
        optimized_code
    )
    
    # Add context-specific optimizations for sustainability
    if context == "sustainability" and "metrics" in function_code:
        optimized_code = re.sub(
            r"return\s+({[^}]+})",
            r"""# Add sustainability metadata
    result = \1
    
    # Add sustainability context
    if "metrics" in result and isinstance(result["metrics"], list):
        for metric in result["metrics"]:
            if "category" in metric and "value" in metric:
                # Add sustainability context based on category
                if metric["category"] == "emissions":
                    metric["sustainability_impact"] = "environmental"
                    if metric.get("value", 0) > 0:
                        metric["carbon_equivalent"] = metric["value"] * 0.85  # Approximate CO2e conversion
                elif metric["category"] == "water":
                    metric["sustainability_impact"] = "environmental"
                elif metric["category"] == "social":
                    metric["sustainability_impact"] = "social"
                elif metric["category"] == "governance":
                    metric["sustainability_impact"] = "governance"
                else:
                    metric["sustainability_impact"] = "unknown"
    
    return result""",
            optimized_code
        )
    
    # Combine imports and optimized code
    final_code = import_section + "\n" + optimized_code.lstrip()
    
    return final_code

# Only import pandas when needed to avoid forcing it as a dependency
def _generate_pandas_analysis(data, analysis_type="trend"):
    """Generate a pandas-based analysis of sustainability data"""
    try:
        import pandas as pd
        
        # Convert data to DataFrame
        df = pd.DataFrame(data)
        
        # Perform requested analysis
        if analysis_type == "trend":
            # Example trend analysis
            result = {
                "trend_direction": "increasing" if df["value"].iloc[-1] > df["value"].iloc[0] else "decreasing",
                "percent_change": ((df["value"].iloc[-1] / df["value"].iloc[0]) - 1) * 100,
                "mean": df["value"].mean(),
                "median": df["value"].median(),
                "std_dev": df["value"].std()
            }
        elif analysis_type == "correlation":
            # Example correlation analysis
            if len(df.columns) >= 2:
                numeric_cols = df.select_dtypes(include=['number']).columns
                if len(numeric_cols) >= 2:
                    result = {
                        "correlation_matrix": df[numeric_cols].corr().to_dict(),
                        "strongest_correlation": df[numeric_cols].corr().unstack().sort_values(ascending=False).drop_duplicates().iloc[1]
                    }
                else:
                    result = {"error": "Not enough numeric columns for correlation analysis"}
            else:
                result = {"error": "Not enough columns for correlation analysis"}
        else:
            result = {"error": f"Unknown analysis type: {analysis_type}"}
        
        return result
    
    except ImportError:
        return {"error": "Pandas not available for advanced analysis"}
    
    except Exception as e:
        return {"error": f"Error in pandas analysis: {str(e)}"}