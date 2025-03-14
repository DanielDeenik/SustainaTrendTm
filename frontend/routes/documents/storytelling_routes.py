"""
Storytelling Routes for SustainaTrend™ Platform

This module provides routes for sustainability storytelling features,
enabling data-driven narrative generation from sustainability metrics.
"""

import logging
import traceback
from datetime import datetime
from typing import Dict, List, Any, Optional

from flask import Blueprint, render_template, request, jsonify, session

# For navigation
try:
    from navigation_config import get_context_for_template
except ImportError:
    # Fallback if navigation is not available
    def get_context_for_template():
        return {}

# Import storytelling components
try:
    from sustainability_storytelling import get_enhanced_stories, get_data_driven_stories
    STORYTELLING_AVAILABLE = True
    logging.info("Storytelling module loaded successfully")
except ImportError as e:
    STORYTELLING_AVAILABLE = False
    logging.warning(f"Storytelling module not available: {str(e)}")

# Create storytelling blueprint
storytelling_bp = Blueprint('hub_storytelling', __name__)

# Configure logging
logger = logging.getLogger(__name__)

@storytelling_bp.route('/storytelling-hub')
def storytelling_hub():
    """
    Storytelling Hub page - central access point for storytelling features
    """
    logger.info("Storytelling Hub route called")
    
    try:
        # Include navigation for the template
        nav_context = get_context_for_template()
        
        # Get storytelling status
        storytelling_status = {
            "storytelling_available": STORYTELLING_AVAILABLE,
        }
        
        # Get stories from storytelling module if available
        if STORYTELLING_AVAILABLE:
            try:
                stories = get_enhanced_stories(audience='all', category='all')
                logger.info(f"Fetched {len(stories)} stories from storytelling module")
            except Exception as e:
                logger.warning(f"Error fetching stories from storytelling module: {str(e)}")
                stories = get_data_driven_stories()
        else:
            # Create a minimal set of mock stories
            stories = [
                {
                    "id": 1,
                    "title": "Carbon Emissions Reduction Success",
                    "content": "Our organization achieved a 15% reduction in carbon emissions over the past quarter.",
                    "category": "emissions"
                },
                {
                    "id": 2,
                    "title": "Water Conservation Initiative Results",
                    "content": "The water conservation program implemented last year has resulted in a 20% decrease in water usage.",
                    "category": "water"
                }
            ]
        
        return render_template(
            "storytelling_hub.html", 
            page_title="Sustainability Storytelling Hub",
            storytelling_status=storytelling_status,
            stories=stories,
            **nav_context
        )
    except Exception as e:
        logger.error(f"Error in storytelling hub route: {str(e)}")
        logger.error(traceback.format_exc())
        
        # Fallback to simpler template
        return render_template(
            "sustainability_stories.html", 
            error=str(e)
        )

@storytelling_bp.route('/api/hub/generate-story', methods=['POST'])
def api_generate_story():
    """API endpoint for generating a sustainability story from the hub"""
    try:
        # Get request data
        data = request.json or {}
        
        # Extract parameters
        metrics = data.get('metrics', [])
        template = data.get('template', 'success')
        topic = data.get('topic', 'sustainability')
        audience = data.get('audience', 'all')
        
        # Check if storytelling module is available
        if not STORYTELLING_AVAILABLE:
            return jsonify({
                'success': False,
                'error': 'Storytelling module is not available'
            }), 500
        
        # Generate stories using the storytelling module
        try:
            stories = get_enhanced_stories(audience=audience, category=topic)
            
            # If stories were generated, return the first one
            if stories:
                return jsonify({
                    'success': True,
                    'story': stories[0]
                })
            else:
                return jsonify({
                    'success': False,
                    'error': 'No stories generated'
                }), 404
        except Exception as e:
            logger.error(f"Error generating story: {str(e)}")
            return jsonify({
                'success': False,
                'error': f'Error generating story: {str(e)}'
            }), 500
    
    except Exception as e:
        logger.error(f"Error in generate story API: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def register_routes(app):
    """
    Register storytelling routes with Flask app
    
    Args:
        app: Flask application
    """
    app.register_blueprint(storytelling_bp, url_prefix='/hub')
    logger.info("Hub storytelling routes registered successfully")