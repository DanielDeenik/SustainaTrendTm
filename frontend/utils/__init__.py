"""
Utils package for SustainaTrend Intelligence Platform
Contains reusable utility functions and modules
"""

# Import all functions from data_providers to make them available at utils.*
from .data_providers import (
    get_api_status,
    get_sustainability_metrics,
    get_sustainability_stories,
    get_sustainability_trends,
    get_ui_suggestions
)