"""
SustainaTrend™ Intelligence Platform - Frontend Package
"""

from .app import create_app
from .routes import api, analytics, base
from .services import (
    mongodb_service,
    document_processor,
    enhanced_search,
    sustainability_copilot,
    sustainability_storytelling,
    sustainability_trend,
    strategy_ai_consultant,
    strategy_simulation,
    monetization_strategies,
    marketing_strategies,
    regulatory_ai_service,
    ethical_ai,
    esrs_framework,
    sentiment_analysis,
    science_based_targets
)

__all__ = [
    'create_app',
    'api',
    'analytics',
    'base',
    'mongodb_service',
    'document_processor',
    'enhanced_search',
    'sustainability_copilot',
    'sustainability_storytelling',
    'sustainability_trend',
    'strategy_ai_consultant',
    'strategy_simulation',
    'monetization_strategies',
    'marketing_strategies',
    'regulatory_ai_service',
    'ethical_ai',
    'esrs_framework',
    'sentiment_analysis',
    'science_based_targets'
]