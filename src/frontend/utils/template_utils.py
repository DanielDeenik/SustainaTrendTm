"""
Template utilities for SustainaTrend™ platform
"""

from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

# Import navigation configuration
try:
    # Try relative import
    from .navigation_config import get_context_for_template as nav_get_context
except ImportError:
    logger.warning("Navigation config module not found, using fallback context")
    
    def nav_get_context():
        """Fallback navigation context function"""
        return {
            "navigation": [],
            "active_nav": None,
            "user": {
                "name": "Demo User",
                "role": "Sustainability Manager"
            }
        }

def get_context_for_template() -> Dict[str, Any]:
    """
    Get common template context including navigation
    
    Returns:
        Dict[str, Any]: Context dictionary for templates
    """
    # Get navigation context
    context = nav_get_context()
    
    # Add common data
    context.update({
        "app_name": "SustainaTrend™",
        "app_version": "2.5.0",
        "year": 2025
    })
    
    return context