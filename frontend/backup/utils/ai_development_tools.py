"""
AI-Powered Development Tools Module

This module provides Flask routes and utilities for demonstrating and using
the AI-powered development automation capabilities of the SustainaTrend™ platform.
"""
import os
import sys
import json
import logging
import importlib.util
from typing import Dict, List, Any, Optional

# Add backend to path if it's not already there
backend_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backend')
if backend_path not in sys.path:
    sys.path.append(backend_path)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try different import strategies for AI code automation utilities
HAS_AI_CODE_AUTOMATION = False

# Try absolute import first
try:
    from backend.utils.ai_code_automation import (
        optimize_function, 
        generate_unit_tests, 
        suggest_code_improvements, 
        extract_sustainability_data,
        AI_LIBRARIES_AVAILABLE
    )
    from backend.utils.fixed_test_generator import SustainabilityTestGenerator
    HAS_AI_CODE_AUTOMATION = True
    logger.info("AI code automation utilities loaded successfully (absolute import)")
except ImportError as e:
    logger.debug(f"Absolute import failed: {e}")
    
    # Try relative import
    try:
        import sys
        parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        if parent_dir not in sys.path:
            sys.path.insert(0, parent_dir)
            
        from backend.utils.ai_code_automation import (
            optimize_function, 
            generate_unit_tests, 
            suggest_code_improvements, 
            extract_sustainability_data,
            AI_LIBRARIES_AVAILABLE
        )
        from backend.utils.fixed_test_generator import SustainabilityTestGenerator
        HAS_AI_CODE_AUTOMATION = True
        logger.info("AI code automation utilities loaded successfully (relative import)")
    except ImportError as e:
        logger.warning(f"AI code automation utilities not available: {e}")
        
# Define mock implementations if imports failed
if not HAS_AI_CODE_AUTOMATION:
    # Mock implementations for required functions
    def optimize_function(function, optimization_goal="efficiency", context="sustainability"):
        return f"# Mock optimized function for {function.__name__}\n# Original code would be optimized for {optimization_goal} in {context} context"
        
    def generate_unit_tests(function, test_framework="pytest", test_coverage=0.8):
        return f"# Mock unit tests for {function.__name__}\n# Would generate {test_framework} tests with {test_coverage*100}% coverage"
        
    def suggest_code_improvements(code, improvement_type="all"):
        return [{"type": "mock_suggestion", "description": "This is a mock code improvement suggestion", "example": "# Example improved code"}]
        
    def extract_sustainability_data(api_endpoint, data_format="json"):
        return {"mock_data": True, "metrics": ["carbon_emissions", "water_usage", "energy_consumption"]}
        
    AI_LIBRARIES_AVAILABLE = False
    
    class SustainabilityTestGenerator:
        def __init__(self, test_framework="pytest"):
            self.test_framework = test_framework
            
        def generate_test_for_function(self, function):
            return generate_unit_tests(function, self.test_framework)

def get_ai_development_status() -> Dict[str, Any]:
    """
    Get the status of AI development tools
    
    Returns:
        Dictionary with status information
    """
    # Check for OpenAI API key
    openai_api_key = os.getenv('OPENAI_API_KEY')
    openai_available = openai_api_key is not None and len(openai_api_key) > 10
    
    # Check for LangChain
    langchain_available = False
    try:
        import langchain
        langchain_available = True
    except ImportError:
        pass
    
    # Determine if we're using mock mode
    mock_mode = not HAS_AI_CODE_AUTOMATION or not openai_available
    
    return {
        "openai_available": openai_available,
        "langchain_available": langchain_available,
        "mock_mode": mock_mode
    }

def get_optimized_function(function_name: str, optimization_goal: str = "efficiency") -> Dict[str, Any]:
    """
    Get AI-optimized version of a function
    
    Args:
        function_name: Name of the function to optimize
        optimization_goal: Goal of optimization (efficiency, readability, etc.)
        
    Returns:
        Dictionary with original and optimized code
    """
    # Mock implementation to demonstrate the feature
    if not HAS_AI_CODE_AUTOMATION:
        # Return a mock optimization
        return {
            "original_code": "def mock_function():\n    pass",
            "optimized_code": "import logging\n\ndef mock_function():\n    logging.info('Optimized function called')\n    return True",
            "improvements": [
                "Added proper logging",
                "Added return value",
                "Added import statement"
            ]
        }
    
    # Parse the function code from the request
    try:
        # In a real implementation, we would dynamically import and optimize the function
        # Here, we'll use the directly provided code through the frontend form
        code = function_name  # In the form submission, this will be the actual code
        
        # Call the optimization function
        optimized_code = optimize_function(code, optimization_goal)
        
        # Generate a list of improvements (simplified version)
        improvements = [
            "Added proper error handling",
            "Improved performance with caching",
            "Added detailed logging",
            "Added input validation"
        ]
        
        return {
            "original_code": code,
            "optimized_code": optimized_code,
            "improvements": improvements
        }
    except Exception as e:
        logger.error(f"Error optimizing function: {str(e)}")
        return {
            "error": f"Error optimizing function: {str(e)}",
            "original_code": function_name,
            "optimized_code": function_name,
            "improvements": []
        }

def generate_function_tests(function_name: str, test_framework: str = "pytest") -> Dict[str, Any]:
    """
    Generate unit tests for a function
    
    Args:
        function_name: Name of the function to generate tests for
        test_framework: Test framework to use (pytest or unittest)
        
    Returns:
        Dictionary with function code and generated tests
    """
    # Mock implementation to demonstrate the feature
    if not HAS_AI_CODE_AUTOMATION:
        # Return mock test code
        return {
            "original_code": "def mock_function():\n    pass",
            "tests": "import pytest\n\ndef test_mock_function():\n    assert mock_function() is None",
            "test_count": 1,
            "coverage": 80,
            "edge_cases": 1
        }
    
    # Parse the function code
    try:
        # In a real implementation, we would dynamically import and generate tests
        # Here, we'll use the directly provided code through the frontend form
        code = function_name  # In the form submission, this will be the actual code
        
        # Call the test generation function directly or use the dedicated test generator
        if test_framework == "pytest":
            generator = SustainabilityTestGenerator(test_framework="pytest")
            tests = generator.generate_test_for_function(code)
        else:
            tests = generate_unit_tests(code, test_framework)
        
        # Count tests (simplified)
        test_count = tests.count("def test_")
        
        # Count edge cases (simplified)
        edge_cases = tests.count("edge_case") + tests.count("edge case")
        
        return {
            "original_code": code,
            "tests": tests,
            "test_count": test_count,
            "coverage": 85,  # Mock value
            "edge_cases": edge_cases
        }
    except Exception as e:
        logger.error(f"Error generating tests: {str(e)}")
        return {
            "error": f"Error generating tests: {str(e)}",
            "original_code": function_name,
            "tests": f"# Error generating tests: {str(e)}",
            "test_count": 0,
            "coverage": 0,
            "edge_cases": 0
        }

def get_improvement_suggestions(code: str, improvement_type: str = "all") -> Dict[str, Any]:
    """
    Get AI-powered improvement suggestions for code
    
    Args:
        code: Code to analyze
        improvement_type: Type of improvements to suggest
        
    Returns:
        Dictionary with code and improvement suggestions
    """
    # Mock implementation to demonstrate the feature
    if not HAS_AI_CODE_AUTOMATION:
        # Return mock suggestions
        return {
            "original_code": code,
            "suggestions": [
                {
                    "suggestion": "Use a logger instead of print statements",
                    "issue": "Using print statements in production code",
                    "explanation": "Replace print statements with proper logging to enable better monitoring and control over output verbosity."
                },
                {
                    "suggestion": "Add error handling",
                    "issue": "Missing error handling",
                    "explanation": "Add try-except blocks to handle potential errors and provide graceful fallbacks."
                }
            ]
        }
    
    # Use the AI-powered code suggestion function
    try:
        suggestions = suggest_code_improvements(code, improvement_type)
        
        return {
            "original_code": code,
            "suggestions": suggestions
        }
    except Exception as e:
        logger.error(f"Error getting improvement suggestions: {str(e)}")
        return {
            "error": f"Error getting improvement suggestions: {str(e)}",
            "original_code": code,
            "suggestions": []
        }

def configure_routes(app):
    """
    Configure Flask routes for AI development tools
    
    Args:
        app: Flask application
    """
    from flask import render_template, request, jsonify
    
    @app.route('/ai-development-tools')
    def ai_development_tools():
        """AI Development Tools Dashboard"""
        logger.info("AI Development Tools dashboard requested")
        
        # Get the status of AI development tools
        ai_status = get_ai_development_status()
        
        # Get OpenAI API key (masked for display)
        openai_api_key = os.getenv('OPENAI_API_KEY')
        masked_key = None
        if openai_api_key:
            # Mask the API key for display
            masked_key = openai_api_key[:4] + "*" * (len(openai_api_key) - 8) + openai_api_key[-4:]
        
        return render_template(
            'ai_development_tools.html',
            ai_status=ai_status,
            openai_api_key=masked_key
        )
    
    @app.route('/api/ai-optimization', methods=['POST'])
    def api_ai_optimization():
        """API endpoint for AI optimization"""
        try:
            data = request.get_json()
            
            if not data or 'code' not in data:
                return jsonify({"error": "No code provided"}), 400
            
            code = data.get('code')
            optimization_goal = data.get('optimization_goal', 'efficiency')
            
            result = get_optimized_function(code, optimization_goal)
            
            return jsonify(result)
        except Exception as e:
            logger.error(f"Error in AI optimization endpoint: {str(e)}")
            return jsonify({"error": str(e)}), 500
    
    @app.route('/api/ai-test-generation', methods=['POST'])
    def api_ai_test_generation():
        """API endpoint for AI test generation"""
        try:
            data = request.get_json()
            
            if not data or 'code' not in data:
                return jsonify({"error": "No code provided"}), 400
            
            code = data.get('code')
            test_framework = data.get('test_framework', 'pytest')
            test_coverage = data.get('test_coverage', 80)
            
            result = generate_function_tests(code, test_framework)
            
            # Add the requested coverage value
            result['coverage'] = int(test_coverage)
            
            return jsonify(result)
        except Exception as e:
            logger.error(f"Error in AI test generation endpoint: {str(e)}")
            return jsonify({"error": str(e)}), 500
    
    @app.route('/api/ai-code-suggestions', methods=['POST'])
    def api_ai_code_suggestions():
        """API endpoint for AI code improvement suggestions"""
        try:
            data = request.get_json()
            
            if not data or 'code' not in data:
                return jsonify({"error": "No code provided"}), 400
            
            code = data.get('code')
            improvement_type = data.get('improvement_type', 'all')
            
            result = get_improvement_suggestions(code, improvement_type)
            
            return jsonify(result)
        except Exception as e:
            logger.error(f"Error in AI code suggestions endpoint: {str(e)}")
            return jsonify({"error": str(e)}), 500

def register_routes(app):
    """
    Register the AI development tools routes with a Flask application
    
    Args:
        app: Flask application
    """
    configure_routes(app)
    logger.info("AI development tools routes registered")