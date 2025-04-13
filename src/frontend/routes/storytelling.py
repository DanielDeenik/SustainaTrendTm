"""
Storytelling Module for SustainaTrend™ Intelligence Platform

This module provides comprehensive AI-powered storytelling features for sustainability data.
It includes story generation, management, and visualization capabilities.
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Union
from flask import Blueprint, jsonify, request, render_template
from werkzeug.exceptions import BadRequest
from ..models.story import Story
from ..services.ai_service import AIService
from ..services.data_service import DataService
from ..utils.error_handler import handle_errors
from ..utils.cache import cache_with_ttl

# Configure logging
logger = logging.getLogger(__name__)

# Initialize blueprint
storytelling_bp = Blueprint('storytelling', __name__)

# Initialize services
ai_service = AIService()
data_service = DataService()

@storytelling_bp.route('/storytelling')
def storytelling_page():
    """Render the storytelling dashboard page."""
    return render_template('storytelling.html')

@storytelling_bp.route('/api/stories', methods=['GET'])
@handle_errors
@cache_with_ttl(ttl=300)  # Cache for 5 minutes
def get_stories():
    """Get all stories with optional filtering."""
    try:
        filters = request.args.to_dict()
        stories = Story.get_all(filters)
        return jsonify({
            'status': 'success',
            'data': [story.to_dict() for story in stories]
        })
        except Exception as e:
        logger.error(f"Error fetching stories: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to fetch stories'
        }), 500

@storytelling_bp.route('/api/stories', methods=['POST'])
@handle_errors
def create_story():
    """Create a new story."""
    try:
        data = request.get_json()
        if not data:
            raise BadRequest("No data provided")

        # Validate required fields
        required_fields = ['title', 'content', 'metrics']
        for field in required_fields:
            if field not in data:
                raise BadRequest(f"Missing required field: {field}")

        # Create story
        story = Story(
            title=data['title'],
            content=data['content'],
            metrics=data['metrics'],
            created_at=datetime.utcnow()
        )
        story.save()

        return jsonify({
            'status': 'success',
            'data': story.to_dict()
        }), 201
    except BadRequest as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400
    except Exception as e:
        logger.error(f"Error creating story: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to create story'
        }), 500

@storytelling_bp.route('/api/stories/<story_id>', methods=['GET'])
@handle_errors
@cache_with_ttl(ttl=300)
def get_story(story_id: str):
    """Get a specific story by ID."""
    try:
        story = Story.get_by_id(story_id)
        if not story:
            return jsonify({
                'status': 'error',
                'message': 'Story not found'
            }), 404

        return jsonify({
            'status': 'success',
            'data': story.to_dict()
        })
    except Exception as e:
        logger.error(f"Error fetching story {story_id}: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to fetch story'
        }), 500

@storytelling_bp.route('/api/stories/<story_id>', methods=['PUT'])
@handle_errors
def update_story(story_id: str):
    """Update a specific story."""
    try:
        data = request.get_json()
        if not data:
            raise BadRequest("No data provided")

        story = Story.get_by_id(story_id)
        if not story:
            return jsonify({
                'status': 'error',
                'message': 'Story not found'
            }), 404

        # Update story fields
        for field, value in data.items():
            if hasattr(story, field):
                setattr(story, field, value)

        story.updated_at = datetime.utcnow()
        story.save()

        return jsonify({
            'status': 'success',
            'data': story.to_dict()
        })
    except BadRequest as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400
    except Exception as e:
        logger.error(f"Error updating story {story_id}: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to update story'
        }), 500

@storytelling_bp.route('/api/stories/<story_id>', methods=['DELETE'])
@handle_errors
def delete_story(story_id: str):
    """Delete a specific story."""
    try:
        story = Story.get_by_id(story_id)
        if not story:
    return jsonify({
                'status': 'error',
                'message': 'Story not found'
            }), 404

        story.delete()
        return jsonify({
            'status': 'success',
            'message': 'Story deleted successfully'
        })
    except Exception as e:
        logger.error(f"Error deleting story {story_id}: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to delete story'
        }), 500

@storytelling_bp.route('/api/stories/generate', methods=['POST'])
@handle_errors
def generate_story():
    """Generate a new story using AI."""
    try:
        data = request.get_json()
        if not data or 'metrics' not in data:
            raise BadRequest("No metrics provided")

        # Generate story using AI service
        story_data = ai_service.generate_story(data['metrics'])
        
        # Create and save story
        story = Story(
            title=story_data['title'],
            content=story_data['content'],
            metrics=data['metrics'],
            created_at=datetime.utcnow()
        )
        story.save()

    return jsonify({
        'status': 'success',
            'data': story.to_dict()
        }), 201
    except BadRequest as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400
            except Exception as e:
        logger.error(f"Error generating story: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to generate story'
        }), 500

@storytelling_bp.route('/api/stories/<story_id>/charts', methods=['GET'])
@handle_errors
@cache_with_ttl(ttl=300)
def get_story_charts(story_id: str):
    """Get chart data for a specific story."""
    try:
        story = Story.get_by_id(story_id)
        if not story:
            return jsonify({
                'status': 'error',
                'message': 'Story not found'
            }), 404
        
        # Generate chart data
        chart_data = data_service.generate_chart_data(story.metrics)
        
        return jsonify({
            'status': 'success',
            'data': chart_data
        })
    except Exception as e:
        logger.error(f"Error generating chart data for story {story_id}: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to generate chart data'
        }), 500

@storytelling_bp.route('/api/stories/templates', methods=['GET'])
@handle_errors
@cache_with_ttl(ttl=3600)  # Cache for 1 hour
def get_story_templates():
    """Get available story templates."""
    try:
        templates = ai_service.get_story_templates()
        return jsonify({
            'status': 'success',
            'data': templates
        })
    except Exception as e:
        logger.error(f"Error fetching story templates: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to fetch story templates'
        }), 500

@storytelling_bp.route('/api/stories/analyze', methods=['POST'])
@handle_errors
def analyze_document():
    """Analyze a document and generate a story."""
    try:
        if 'file' not in request.files:
            raise BadRequest("No file provided")

        file = request.files['file']
        if not file.filename:
            raise BadRequest("No file selected")

        # Analyze document using AI service
        analysis_result = ai_service.analyze_document(file)
        
        # Generate story from analysis
        story_data = ai_service.generate_story_from_analysis(analysis_result)
        
        # Create and save story
        story = Story(
            title=story_data['title'],
            content=story_data['content'],
            metrics=analysis_result['metrics'],
            created_at=datetime.utcnow()
        )
        story.save()

        return jsonify({
            'status': 'success',
            'data': {
                'story': story.to_dict(),
                'analysis': analysis_result
            }
        }), 201
    except BadRequest as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400
    except Exception as e:
        logger.error(f"Error analyzing document: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to analyze document'
        }), 500