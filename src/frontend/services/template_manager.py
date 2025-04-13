"""
Template Manager Module for SustainaTrend™

This module provides template management services for the SustainaTrend™ platform.
It handles template loading, rendering, and caching.
"""

import os
import logging
import json
from typing import Dict, Any, Optional
from datetime import datetime

# Setup logging
logger = logging.getLogger("services.template_manager")

class TemplateManager:
    """
    Template management service for handling UI templates.
    Provides caching and template selection logic.
    """
    
    def __init__(self, template_dir: str = "templates"):
        """
        Initialize the template manager
        
        Args:
            template_dir: Directory containing templates
        """
        self.template_dir = template_dir
        self.template_cache = {}
        self.last_modified = {}
        logger.info(f"Template manager initialized with template directory: {template_dir}")
    
    def get_template_path(self, template_name: str) -> str:
        """
        Get the full path to a template
        
        Args:
            template_name: Name of the template
            
        Returns:
            Full path to the template file
        """
        # Handle templates with or without extension
        if not template_name.endswith(".html"):
            template_name = f"{template_name}.html"
            
        # Create full path
        return os.path.join(self.template_dir, template_name)
    
    def get_template(self, template_name: str, use_cache: bool = True) -> Optional[str]:
        """
        Get a template by name
        
        Args:
            template_name: Name of the template to load
            use_cache: Whether to use cached templates
            
        Returns:
            Template content as string, or None if not found
        """
        template_path = self.get_template_path(template_name)
        
        # Check if template exists
        if not os.path.exists(template_path):
            logger.warning(f"Template not found: {template_path}")
            return None
            
        # Check if we can use cached version
        if use_cache and template_name in self.template_cache:
            last_modified = os.path.getmtime(template_path)
            if last_modified <= self.last_modified.get(template_name, 0):
                logger.debug(f"Using cached template: {template_name}")
                return self.template_cache[template_name]
                
        # Load template from file
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Update cache
            if use_cache:
                self.template_cache[template_name] = content
                self.last_modified[template_name] = os.path.getmtime(template_path)
                
            logger.debug(f"Loaded template: {template_name}")
            return content
        except Exception as e:
            logger.error(f"Error loading template {template_name}: {str(e)}")
            return None
    
    def render_template(self, template_name: str, context: Dict[str, Any]) -> Optional[str]:
        """
        Render a template with the given context
        This is a simple template renderer for demonstration purposes.
        In a real application, use Flask or Jinja2 for template rendering.
        
        Args:
            template_name: Name of the template to render
            context: Dictionary of variables to use in the template
            
        Returns:
            Rendered template as string, or None if rendering failed
        """
        # Get template content
        template_content = self.get_template(template_name)
        if not template_content:
            return None
            
        # Simple variable substitution
        rendered = template_content
        for key, value in context.items():
            placeholder = f"{{{{{key}}}}}"
            rendered = rendered.replace(placeholder, str(value))
            
        return rendered
    
    def get_available_templates(self) -> Dict[str, Dict[str, Any]]:
        """
        Get list of available templates with metadata
        
        Returns:
            Dictionary mapping template names to metadata
        """
        templates = {}
        
        # Scan template directory
        if os.path.exists(self.template_dir):
            for filename in os.listdir(self.template_dir):
                if filename.endswith(".html"):
                    template_name = filename.replace(".html", "")
                    template_path = os.path.join(self.template_dir, filename)
                    
                    # Get template metadata
                    templates[template_name] = {
                        "name": template_name,
                        "path": template_path,
                        "size": os.path.getsize(template_path),
                        "last_modified": datetime.fromtimestamp(
                            os.path.getmtime(template_path)
                        ).isoformat()
                    }
        
        return templates