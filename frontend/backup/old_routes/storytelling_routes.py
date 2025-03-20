"""
Storytelling Routes for SustainaTrend™ Platform (DEPRECATED)

This module provides routes for sustainability storytelling features,
enabling data-driven narrative generation from sustainability metrics.

WARNING: This module is deprecated and will be removed in a future version.
         Please use the new modular implementation in 'routes/storytelling.py' instead.
"""

import logging
import traceback
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional

from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for

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
logger.warning("DEPRECATED: The hub_storytelling blueprint is deprecated and will be removed in a future version.")

# Configure logging
logger = logging.getLogger(__name__)

@storytelling_bp.route('/storytelling-hub')
def storytelling_hub():
    """
    Storytelling Hub page - redirects to the new modular implementation
    """
    logger.warning("DEPRECATED: Accessing old storytelling hub route - redirecting to new implementation")
    
    # Redirect to the new storytelling implementation
    try:
        return redirect(url_for('storytelling.storytelling_home'))
    except Exception as e:
        logger.error(f"Error redirecting to new storytelling implementation: {str(e)}")
        logger.error(traceback.format_exc())
        
        # Fallback - try direct redirect
        return redirect('/storytelling/')

@storytelling_bp.route('/api/hub/generate-story', methods=['POST'])
def api_generate_story():
    """
    API endpoint for generating a sustainability story from the hub
    DEPRECATED: This endpoint forwards to the new implementation
    """
    logger.warning("DEPRECATED: Using old API endpoint for story generation - forwarding to new implementation")
    
    try:
        # Get request data
        data = request.json or {}
        
        # Extract parameters and forward to the new endpoint
        audience = data.get('audience', 'all')
        topic = data.get('topic', 'sustainability') # This was 'category' in the new implementation
        
        # Create a UUID for the story
        story_id = str(uuid.uuid4())
        
        # Return a notice about the API endpoint being deprecated
        return jsonify({
            'success': True,
            'deprecated': True,
            'message': 'This API endpoint is deprecated. Please use /storytelling/api/stories/generate instead.',
            'story': {
                'id': story_id,
                'title': f'Story request forwarded to new API: {topic}',
                'content': 'Please check the new API endpoint for results.',
                'audience': audience,
                'category': topic,
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        })
    
    except Exception as e:
        logger.error(f"Error in deprecated generate story API: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': str(e),
            'deprecated': True,
            'message': 'This API endpoint is deprecated. Please use /storytelling/api/stories/generate instead.'
        }), 500

def register_routes(app):
    """
    Register legacy storytelling routes with Flask app
    DEPRECATED: This function is kept for backward compatibility
    
    Args:
        app: Flask application
    """
    app.register_blueprint(storytelling_bp, url_prefix='/hub')
    logger.warning("DEPRECATED: Hub storytelling routes registered - these routes will be removed in a future version. Please use the new modular implementation.")