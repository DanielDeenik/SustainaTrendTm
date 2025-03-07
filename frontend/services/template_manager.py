"""
Template Manager for SustainaTrend™

This module provides functions to standardize template rendering and management.
It enforces consistent use of the base_new.html template and template variables.
"""

import logging
from typing import Dict, Any, Optional, List
from flask import render_template  # type: ignore

# Configure logging
logger = logging.getLogger(__name__)

class TemplateManager:
    """Manager class for standardized template handling"""
    
    # Base template to use consistently across the application
    BASE_TEMPLATE = "base_new.html"
    
    # Default page titles for common pages
    DEFAULT_TITLES = {
        "dashboard": "Dashboard | SustainaTrend™",
        "search": "Search | SustainaTrend™",
        "trend_analysis": "Trend Analysis | SustainaTrend™",
        "analytics": "Analytics | SustainaTrend™",
        "sustainability": "Sustainability | SustainaTrend™",
        "storytelling": "Sustainability Storytelling | SustainaTrend™",
        "monetization": "Monetization | SustainaTrend™",
        "settings": "Settings | SustainaTrend™"
    }
    
    @classmethod
    def get_base_context(cls, page_id: str, title: Optional[str] = None) -> Dict[str, Any]:
        """
        Get base context dictionary for template rendering
        
        Args:
            page_id: ID of the current page (for navigation highlighting)
            title: Page title (defaults to standard title based on page_id)
            
        Returns:
            Base context dictionary
        """
        # Get default title based on page_id or use provided title
        page_title = title or cls.DEFAULT_TITLES.get(page_id, "SustainaTrend™")
        
        return {
            "page_id": page_id,
            "title": page_title,
            "show_header": True,
            "show_footer": True,
            "show_sidebar": True,
            # Common UI settings
            "show_search": True,
            "show_actions": True,
            "show_export": True,
            "show_filter": True,
            # Theme-related context (could be expanded later)
            "theme": {
                "primary_color": "var(--primary-color)",
                "secondary_color": "var(--secondary-color)",
                "text_color": "var(--text-color)",
                "bg_color": "var(--bg-body)"
            }
        }
    
    @classmethod
    def render(
        cls, 
        template_name: str, 
        page_id: str,
        title: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Render a template with standardized context
        
        Args:
            template_name: Name of the template to render
            page_id: ID of the current page (for navigation highlighting)
            title: Page title (optional)
            **kwargs: Additional template variables
            
        Returns:
            Rendered template
        """
        # Get base context and merge with provided kwargs
        context = cls.get_base_context(page_id, title)
        context.update(kwargs)
        
        # Log template rendering
        logger.debug(f"Rendering template {template_name} for page {page_id}")
        
        return render_template(template_name, **context)
    
    @classmethod
    def render_dashboard(cls, metrics: List[Dict[str, Any]], **kwargs) -> str:
        """
        Render the dashboard template with metrics data
        
        Args:
            metrics: List of metrics data
            **kwargs: Additional template variables
            
        Returns:
            Rendered dashboard template
        """
        return cls.render("dashboard_new.html", "dashboard", **kwargs)
    
    @classmethod
    def render_trend_analysis(cls, trends: List[Dict[str, Any]], **kwargs) -> str:
        """
        Render the trend analysis template with trends data
        
        Args:
            trends: List of trends data
            **kwargs: Additional template variables
            
        Returns:
            Rendered trend analysis template
        """
        return cls.render("trend_analysis.html", "trend_analysis", **kwargs)
    
    @classmethod
    def render_analytics(cls, **kwargs) -> str:
        """
        Render the analytics dashboard template
        
        Args:
            **kwargs: Template variables
            
        Returns:
            Rendered analytics template
        """
        return cls.render("analytics_dashboard.html", "analytics", **kwargs)
    
    @classmethod
    def render_search(cls, query: str, results: List[Dict[str, Any]], **kwargs) -> str:
        """
        Render the search template with search results
        
        Args:
            query: Search query
            results: Search results
            **kwargs: Additional template variables
            
        Returns:
            Rendered search template
        """
        return cls.render("search.html", "search", query=query, results=results, **kwargs)
    
    @classmethod
    def render_error(cls, error_code: int, message: str, **kwargs) -> str:
        """
        Render an error template
        
        Args:
            error_code: HTTP error code
            message: Error message
            **kwargs: Additional template variables
            
        Returns:
            Rendered error template
        """
        return cls.render(
            "error.html", 
            "error",
            title=f"Error {error_code} | SustainaTrend™",
            error_code=error_code,
            error_message=message,
            **kwargs
        )