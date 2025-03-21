"""
Stories Module for SustainaTrend™ Intelligence Platform

This module provides comprehensive AI-powered storytelling features using a modular
implementation with full compatibility with the platform's dark theme and Finchat-inspired UI.

Key features:
1. Unified storytelling interface with consistent styling
2. Multiple story generation templates (climate, ESG, compliance, etc.)
3. Custom story creation with stakeholder-specific options
4. Story history and management
5. Integration with document analysis
6. Visual chart generation
"""

import logging
import uuid
import json
from datetime import datetime
from typing import Dict, List, Any, Optional, Union

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, current_app
from flask import session, g

# Import sustainability storytelling utilities
from frontend.sustainability_storytelling import get_enhanced_stories, get_lcm_story, get_data_driven_stories
from frontend.navigation_config import get_context_for_template

# Create blueprint
stories_bp = Blueprint('stories', __name__, url_prefix='/stories')

# Configure logging
logger = logging.getLogger(__name__)

@stories_bp.route('/')
def stories_home():
    """Main stories dashboard with AI-powered storytelling features"""
    # Get query parameters
    audience = request.args.get('audience', 'all')
    category = request.args.get('category', 'all')
    
    # Set up template context with navigation
    template_context = get_context_for_template()
    
    # Generate stories for initial display
    try:
        stories = get_enhanced_stories(audience, category)
        logger.info(f"Generated {len(stories)} enhanced stories for Stories dashboard")
    except Exception as e:
        logger.error(f"Error generating stories: {str(e)}")
        stories = []
    
    # Add stories to template context
    template_context.update({
        'stories': stories,
        'audience': audience,
        'category': category,
        'page_title': 'Sustainability Stories',
        'active_section': 'stories'
    })
    
    return render_template('strategy/storytelling.html', **template_context)

@stories_bp.route('/create')
def create_story():
    """Create a new sustainability story with AI assistance"""
    # Set up template context with navigation
    template_context = get_context_for_template()
    
    # Add required context
    template_context.update({
        'page_title': 'Create Story',
        'active_section': 'stories',
        'templates': get_story_templates()
    })
    
    return render_template('strategy/storytelling_create.html', **template_context)

@stories_bp.route('/view/<story_id>')
def view_story(story_id):
    """View a specific sustainability story"""
    # Set up template context with navigation
    template_context = get_context_for_template()
    
    # Try to retrieve the story from session history first
    stories_history = session.get('stories_history', [])
    story = next((s for s in stories_history if s.get('id') == story_id), None)
    
    # If not found in history, generate a new story
    if not story:
        try:
            # Generate a new story
            story = get_lcm_story(story_id=story_id)
            logger.info(f"Generated new story with ID {story_id}")
        except Exception as e:
            logger.error(f"Error retrieving story {story_id}: {str(e)}")
            # Return to stories home with error
            return redirect(url_for('stories.stories_home'))
    
    # Add story to template context
    template_context.update({
        'story': story,
        'page_title': story.get('title', 'Sustainability Story'),
        'active_section': 'stories'
    })
    
    return render_template('strategy/story_detail.html', **template_context)

@stories_bp.route('/api/generate', methods=['POST'])
def api_generate_story():
    """API endpoint for story generation"""
    if not request.is_json:
        return jsonify({"success": False, "error": "Request must be JSON"}), 400
    
    data = request.get_json()
    
    # Get required parameters
    template = data.get('template')
    audience = data.get('audience', 'all')
    category = data.get('category', 'all') 
    custom_prompt = data.get('prompt')
    
    # Generate story ID if not provided
    story_id = data.get('story_id', str(uuid.uuid4()))
    
    try:
        # Generate story using LCM
        story = get_lcm_story(
            audience=audience,
            category=category,
            prompt=custom_prompt,
            document_data=data.get('document_data')
        )
        
        # Add story to session history
        stories_history = session.get('stories_history', [])
        stories_history.append(story)
        session['stories_history'] = stories_history[-10:]  # Keep last 10 stories
        
        return jsonify({
            "success": True,
            "story": story
        })
    except Exception as e:
        logger.error(f"Error generating story: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@stories_bp.route('/api/stories')
def api_get_stories():
    """API endpoint for fetching stories"""
    # Get query parameters
    audience = request.args.get('audience', 'all')
    category = request.args.get('category', 'all')
    format_type = request.args.get('format', 'json')
    
    try:
        # Generate stories
        stories = get_enhanced_stories(audience, category)
        
        if format_type == 'html':
            # Generate HTML story cards
            html_content = render_template(
                'partials/story_cards_content.html',
                stories=stories
            )
            return jsonify({
                'success': True,
                'html': html_content,
                'count': len(stories)
            })
        else:
            # Return JSON data
            return jsonify({
                'success': True,
                'stories': stories,
                'count': len(stories),
                'filters': {
                    'audience': audience,
                    'category': category
                }
            })
    except Exception as e:
        logger.error(f"Error retrieving stories: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@stories_bp.route('/api/story/<story_id>')
def api_get_story(story_id):
    """API endpoint for fetching a specific story"""
    try:
        # Try to retrieve from session history first
        stories_history = session.get('stories_history', [])
        story = next((s for s in stories_history if s.get('id') == story_id), None)
        
        # If not found in history, generate a new story
        if not story:
            story = get_lcm_story(story_id=story_id)
        
        return jsonify({
            'success': True,
            'story': story
        })
    except Exception as e:
        logger.error(f"Error retrieving story {story_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@stories_bp.route('/test-redirects')
def test_redirects():
    """Test page for storytelling redirects"""
    # Set up template context with navigation
    template_context = get_context_for_template()
    
    # Add page context
    template_context.update({
        'page_title': 'Test Storytelling Redirects',
        'active_section': 'stories'
    })
    
    return render_template('test_storytelling_redirect.html', **template_context)

@stories_bp.route('/api/templates')
def api_get_templates():
    """API endpoint for getting story templates"""
    try:
        templates = get_story_templates()
        return jsonify({
            'success': True,
            'templates': templates
        })
    except Exception as e:
        logger.error(f"Error retrieving templates: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@stories_bp.route('/api/chart', methods=['POST'])
def api_generate_chart():
    """API endpoint for generating story charts"""
    if not request.is_json:
        return jsonify({"success": False, "error": "Request must be JSON"}), 400
    
    data = request.get_json()
    
    # Get required parameters
    story_id = data.get('story_id')
    chart_type = data.get('chart_type', 'line')
    
    if not story_id:
        return jsonify({"success": False, "error": "Missing story_id parameter"}), 400
    
    try:
        # Generate chart based on story data
        chart_data = generate_story_chart(story_id, chart_type)
        
        return jsonify({
            "success": True,
            "chart_data": chart_data
        })
    except Exception as e:
        logger.error(f"Error generating chart: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# Utility functions

def get_story_templates() -> List[Dict[str, Any]]:
    """Get available story templates"""
    return [
        {
            "id": "climate-action",
            "title": "Climate Action Narrative",
            "description": "Tell your climate action story, highlighting emissions reductions, renewable energy transitions, and progress toward targets.",
            "icon": "fas fa-globe-americas",
            "metrics": ["Emissions", "Renewable Energy", "Climate Targets"],
            "audience": ["executives", "investors", "regulators"]
        },
        {
            "id": "esg-report",
            "title": "ESG Performance Summary",
            "description": "Summarize your environmental, social, and governance performance for stakeholders with key metrics and achievements.",
            "icon": "fas fa-chart-line",
            "metrics": ["ESG Scores", "Governance", "Social Impact"],
            "audience": ["investors", "executives", "employees"]
        },
        {
            "id": "compliance",
            "title": "Regulatory Compliance Story",
            "description": "Showcase your compliance with sustainability regulations like CSRD, SEC climate rules, or ISSB standards.",
            "icon": "fas fa-clipboard-check",
            "metrics": ["CSRD", "ISSB", "SEC"],
            "audience": ["regulators", "investors", "executives"]
        },
        {
            "id": "water",
            "title": "Water Stewardship Narrative",
            "description": "Highlight your water conservation efforts, reduction in water intensity, and watershed protection initiatives.",
            "icon": "fas fa-tint",
            "metrics": ["Water Usage", "Water Risk", "Conservation"],
            "audience": ["investors", "regulators", "employees"]
        },
        {
            "id": "biodiversity",
            "title": "Biodiversity Impact Story",
            "description": "Share your organization's approach to biodiversity protection and nature-positive initiatives.",
            "icon": "fas fa-seedling",
            "metrics": ["Biodiversity", "Land Use", "Ecosystem"],
            "audience": ["regulators", "investors", "general-public"]
        },
        {
            "id": "circular",
            "title": "Circular Economy Narrative",
            "description": "Demonstrate your progress toward circular business models, waste reduction, and materials efficiency.",
            "icon": "fas fa-recycle",
            "metrics": ["Waste", "Recycling", "Circularity"],
            "audience": ["investors", "customers", "employees"]
        }
    ]

def generate_story_chart(story_id: str, chart_type: str = 'line') -> Dict[str, Any]:
    """Generate chart data for a story"""
    # Try to get story from session history
    stories_history = session.get('stories_history', [])
    story = next((s for s in stories_history if s.get('id') == story_id), None)
    
    # If not in history, use default data
    if not story:
        return get_default_chart_data(chart_type)
    
    # Get category from story for appropriate data generation
    category = story.get('category', 'emissions')
    
    # Import chart generation function if available
    try:
        from frontend.sustainability_storytelling import generate_chart_data
        return generate_chart_data(category, 'quarterly', chart_type)
    except ImportError:
        # Fallback to default chart data
        return get_default_chart_data(chart_type)

def get_default_chart_data(chart_type: str) -> Dict[str, Any]:
    """Generate default chart data as fallback"""
    if chart_type == 'line':
        return {
            'type': 'line',
            'data': {
                'labels': ['Q1', 'Q2', 'Q3', 'Q4'],
                'datasets': [{
                    'label': 'Sustainability Metric',
                    'data': [65, 59, 80, 81],
                    'fill': False,
                    'borderColor': 'rgb(75, 192, 192)',
                    'tension': 0.1
                }]
            }
        }
    elif chart_type == 'bar':
        return {
            'type': 'bar',
            'data': {
                'labels': ['Category 1', 'Category 2', 'Category 3', 'Category 4'],
                'datasets': [{
                    'label': 'Sustainability Metric',
                    'data': [65, 59, 80, 81],
                    'backgroundColor': [
                        'rgba(255, 99, 132, 0.2)',
                        'rgba(255, 159, 64, 0.2)',
                        'rgba(255, 205, 86, 0.2)',
                        'rgba(75, 192, 192, 0.2)'
                    ],
                    'borderColor': [
                        'rgb(255, 99, 132)',
                        'rgb(255, 159, 64)',
                        'rgb(255, 205, 86)',
                        'rgb(75, 192, 192)'
                    ],
                    'borderWidth': 1
                }]
            }
        }
    else:
        return {
            'type': 'pie',
            'data': {
                'labels': ['Category 1', 'Category 2', 'Category 3', 'Category 4'],
                'datasets': [{
                    'label': 'Sustainability Metric',
                    'data': [65, 59, 80, 81],
                    'backgroundColor': [
                        'rgba(255, 99, 132, 0.5)',
                        'rgba(54, 162, 235, 0.5)',
                        'rgba(255, 206, 86, 0.5)',
                        'rgba(75, 192, 192, 0.5)'
                    ],
                    'borderWidth': 1
                }]
            }
        }

def register_blueprint(app):
    """Register Stories blueprint with Flask app"""
    app.register_blueprint(stories_bp)
    logger.info("Stories blueprint registered successfully")