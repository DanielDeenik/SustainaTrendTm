"""
Storytelling Blueprint for SustainaTrend™ Intelligence Platform

This module provides a dedicated, modular implementation of the AI Storytelling
capabilities with LCM-inspired (Latent Concept Models) principles.

Key features:
1. UUID-based story identification system
2. Clean blueprint architecture
3. AI agent integration for dynamic story generation
4. API-driven interaction model
5. Consolidated template handling via template_type
"""
import logging
import uuid
import sys
import os
from datetime import datetime
from typing import Dict, List, Any, Optional

# Ensure paths are configured correctly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import Flask modules
from flask import Blueprint, render_template, request, jsonify, current_app, url_for, redirect

# Import sustainability storytelling utilities
from sustainability_storytelling import get_enhanced_stories
from navigation_config import get_context_for_template

# Configure logging
logger = logging.getLogger(__name__)

# Create Blueprint
storytelling_bp = Blueprint('storytelling', __name__, url_prefix='/storytelling')

# Constants
STORYTELLING_AVAILABLE = True  # Flag to control feature availability
DEFAULT_TEMPLATE = "strategy/storytelling.html"  # Default template
UNIFIED_TEMPLATE = "finchat_dark_dashboard.html"  # Unified dashboard template

# AI Storytelling Agent Functions
def get_ai_generated_story(story_id: str, audience: str = 'all', category: str = 'all', prompt: str = '') -> Dict[str, Any]:
    """
    Get AI-generated story using LCM-inspired principles
    
    Args:
        story_id: UUID for the story
        audience: Target audience for the story
        category: Sustainability category
        prompt: Custom prompt for story generation
        
    Returns:
        Generated story dictionary
    """
    logger.info(f"Generating AI story with id={story_id}, audience={audience}, category={category}")
    
    # Use enhanced stories function from sustainability_storytelling module
    stories = get_enhanced_stories(audience=audience, category=category, prompt=prompt)
    
    if stories and len(stories) > 0:
        # Get the first story and ensure it has the correct ID
        story = stories[0]
        story['id'] = story_id
        
        # Add timestamp if not present
        if 'timestamp' not in story:
            story['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
        return story
    else:
        # Create a minimal fallback story if generation fails
        return {
            "id": story_id,
            "title": f"Story for {audience} on {category}",
            "content": "Unable to generate story content at this time.",
            "category": category,
            "audience": audience,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

# Routes
@storytelling_bp.route('/', methods=['GET'])
def storytelling_hub():
    """
    Main storytelling hub page
    """
    logger.info("Storytelling hub accessed")
    
    # Get parameters
    audience = request.args.get('audience', 'all')
    category = request.args.get('category', 'all')
    
    # Generate a new story ID
    story_id = str(uuid.uuid4())
    
    # Get navigation context
    nav_context = get_context_for_template()
    
    # Get AI-generated stories
    stories = get_enhanced_stories(audience=audience, category=category)
    
    # Render the unified template with template_type=storytelling
    return render_template(
        'strategy/storytelling.html',
        page_title="AI Storytelling Hub",
        active_nav="storytelling",
        stories=stories,
        story_id=story_id,
        selected_audience=audience,
        selected_category=category,
        template_type='storytelling',
        storytelling_available=STORYTELLING_AVAILABLE,
        **nav_context
    )

@storytelling_bp.route('/create', methods=['GET', 'POST'])
def create_story():
    """
    Create a new story using AI agent
    """
    if request.method == 'POST':
        # Get form data
        audience = request.form.get('audience', 'all')
        category = request.form.get('category', 'all')
        prompt = request.form.get('prompt', '')
        
        # Generate a new story ID
        story_id = str(uuid.uuid4())
        
        # Generate story with AI agent
        story = get_ai_generated_story(story_id, audience, category, prompt)
        
        # Redirect to view the generated story
        return redirect(url_for('storytelling.view_story', story_id=story_id))
    else:
        # Show story creation form
        nav_context = get_context_for_template()
        
        return render_template(
            'strategy/storytelling_create.html',
            page_title="Create AI Story",
            active_nav="storytelling",
            template_type='storytelling_create',
            **nav_context
        )

@storytelling_bp.route('/view/<story_id>', methods=['GET'])
def view_story(story_id):
    """
    View a specific story by ID
    """
    logger.info(f"Viewing story with id={story_id}")
    
    # In a production environment, we would retrieve the story from a database
    # For this implementation, we'll generate a story with the given ID
    audience = request.args.get('audience', 'all')
    category = request.args.get('category', 'all')
    
    # Get AI-generated story
    story = get_ai_generated_story(story_id, audience, category)
    
    # Get navigation context
    nav_context = get_context_for_template()
    
    # Render the story view template
    return render_template(
        'strategy/storytelling_view.html',
        page_title=f"Story: {story['title']}",
        active_nav="storytelling",
        story=story,
        template_type='storytelling_view',
        **nav_context
    )

# API Endpoints
@storytelling_bp.route('/api/generate', methods=['POST'])
def api_generate_story():
    """
    API endpoint for generating a story
    """
    logger.info("API story generation endpoint called")
    
    # Validate request
    if not request.is_json:
        return jsonify({
            'error': True,
            'message': 'Invalid request format. JSON required.'
        }), 400
        
    # Get request data
    data = request.json
    
    # Extract parameters
    audience = data.get('audience')
    category = data.get('category')
    prompt = data.get('prompt')
    
    # Validate required parameters
    if not all([audience, category, prompt]):
        return jsonify({
            'error': True,
            'message': 'Missing required parameters. Please provide audience, category, and prompt.'
        }), 400
    
    # Generate a new story ID
    story_id = str(uuid.uuid4())
    
    # Generate story with AI agent
    story = get_ai_generated_story(story_id, audience, category, prompt)
    
    # Return the generated story
    return jsonify(story)

@storytelling_bp.route('/api/stories', methods=['GET'])
def api_get_stories():
    """
    API endpoint for getting stories
    """
    logger.info("API get stories endpoint called")
    
    # Get parameters
    audience = request.args.get('audience', 'all')
    category = request.args.get('category', 'all')
    
    # Get stories
    stories = get_enhanced_stories(audience=audience, category=category)
    
    # Return the stories
    return jsonify({
        'success': True,
        'stories': stories,
        'count': len(stories)
    })

# Function to register the blueprint
def register_storytelling_blueprint(app):
    """
    Register the storytelling blueprint with the application
    
    Args:
        app: Flask application
    """
    app.register_blueprint(storytelling_bp)
    logger.info("Storytelling blueprint registered successfully")