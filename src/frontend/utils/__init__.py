"""
Utilities Package for SustainaTrend™

This package provides utility functions and services used across the platform.
"""

from .template_utils import get_context_for_template
from .data_providers import (
    get_metrics,
    get_trends,
    get_stories,
    get_monetization_strategies
)

__all__ = [
    'get_context_for_template',
    'get_metrics',
    'get_trends',
    'get_stories',
    'get_monetization_strategies'
]

# This file is intentionally empty to make the directory a proper Python package