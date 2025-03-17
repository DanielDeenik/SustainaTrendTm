"""
Navigation Configuration for SustainaTrend™ Minimal UI

This module defines the navigation structure for the minimal, AI-driven
storytelling interface with a focus on clear data visualization.
"""
from typing import Dict, List, Any

def get_navigation_structure():
    """
    Returns the complete navigation structure for the SustainaTrend™ platform.
    
    Each navigation item contains:
    - id: Unique identifier for the nav item
    - title: Display name
    - url: URL path
    - icon: Icon name/path
    - section: Section the nav item belongs to
    
    Returns:
        dict: Complete navigation structure
    """
    navigation = {
        "sections": [
            {
                "id": "core",
                "title": "Core",
                "items": [
                    {
                        "id": "home",
                        "title": "Home",
                        "url": "/",
                        "icon": "fa-home"
                    },
                    {
                        "id": "dashboard",
                        "title": "Dashboard",
                        "url": "/dashboard",
                        "icon": "fa-chart-bar"
                    },
                    {
                        "id": "risk",
                        "title": "Risk Tracker",
                        "url": "/risk-tracker",
                        "icon": "fa-exclamation-triangle"
                    },
                    {
                        "id": "analytics",
                        "title": "Analytics",
                        "url": "/analytics-dashboard",
                        "icon": "fa-chart-line"
                    }
                ]
            },
            {
                "id": "insights",
                "title": "Insights",
                "items": [
                    {
                        "id": "stories",
                        "title": "AI Storytelling Engine",
                        "url": "/storytelling/",
                        "icon": "fa-newspaper"
                    },
                    {
                        "id": "trends",
                        "title": "Trend Analysis",
                        "url": "/trend-analysis",
                        "icon": "fa-chart-bar"
                    },
                    {
                        "id": "virality",
                        "title": "Virality Metrics",
                        "url": "/virality-metrics",
                        "icon": "fa-chart-network"
                    },
                    {
                        "id": "strategy",
                        "title": "Strategy Hub",
                        "url": "/unified-strategy-hub",
                        "icon": "fa-chess-board",
                        "badge": "New",
                        "badge_color": "success",
                        "description": "Unified strategy, simulation & monetization center"
                    },
                    {
                        "id": "regulatory_ai",
                        "title": "Regulatory AI Agent",
                        "url": "/regulatory-ai/",
                        "icon": "fa-balance-scale",
                        "badge": "New",
                        "badge_color": "danger",
                        "description": "AI-powered regulatory compliance assessment"
                    },
                    {
                        "id": "strategy-modeling",
                        "title": "Strategy Modeling",
                        "url": "/strategy-modeling-tool",
                        "icon": "fa-chart-line",
                        "badge": "New",
                        "badge_color": "primary",
                        "description": "Interactive strategy modeling with visualizations"
                    }
                ]
            },
            {
                "id": "tools",
                "title": "Tools",
                "items": [
                    {
                        "id": "documents",
                        "title": "Upload Reports",
                        "url": "/pdf-analyzer",
                        "icon": "fa-file-upload"
                    },
                    {
                        "id": "ethical_ai",
                        "title": "Ethical AI Assessment",
                        "url": "/document-upload",
                        "icon": "fa-balance-scale"
                    },
                    {
                        "id": "terminal",
                        "title": "Data Terminal",
                        "url": "/data-terminal",
                        "icon": "fa-terminal"
                    },
                    {
                        "id": "copilot",
                        "title": "AI Co-Pilot",
                        "url": "/co-pilot",
                        "icon": "fa-robot"
                    },
                    {
                        "id": "realestate",
                        "title": "Real Estate",
                        "url": "/real-estate",
                        "icon": "fa-building"
                    }
                ]
            }
        ],
        "user_menu": [
            {
                "id": "settings",
                "title": "Settings",
                "url": "#",
                "icon": "fa-cog"
            },
            {
                "id": "help",
                "title": "Help & Support",
                "url": "#",
                "icon": "fa-question-circle"
            },
            {
                "id": "debug",
                "title": "Debug",
                "url": "/debug",
                "icon": "fa-bug"
            }
        ]
    }
    
    return navigation

def get_context_for_template():
    """
    Prepare the navigation context for Flask templates.
    
    Returns:
        dict: Navigation context for the templates
    """
    navigation = get_navigation_structure()
    
    # Extract sections and user menu for template
    nav_sections = navigation["sections"]
    user_menu = navigation["user_menu"]
    
    return {
        "nav_sections": nav_sections,
        "user_menu": user_menu,
        "nav_structure": navigation  # Add complete navigation structure for debug view
    }