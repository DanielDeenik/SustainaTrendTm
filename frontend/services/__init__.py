"""
SustainaTrend™ Services Package

This package contains service-layer implementations for data access and business logic.
"""

from frontend.services.mongodb_service import MongoDBService
from frontend.services.template_manager import TemplateManager

__all__ = ['MongoDBService', 'TemplateManager']