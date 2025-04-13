"""
SustainaTrend™ Intelligence Platform - Routes Package
"""

from flask import Blueprint

# Import route modules
from . import main
from . import auth
from . import vc_dashboard

__all__ = [
    'main',
    'auth',
    'vc_dashboard'
]