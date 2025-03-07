"""
SustainaTrend™ Services Package

This package contains service-layer implementations for data access and business logic.
"""

from .template_manager import TemplateManager
from .simple_mock_service import SimpleMockService

__all__ = ['SimpleMockService', 'TemplateManager']