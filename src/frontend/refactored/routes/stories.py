"""
Storytelling routes for the SustainaTrend™ Platform.
"""
from flask import Blueprint, render_template, jsonify, request, current_app
from src.frontend.refactored.services.mongodb_service import MongoDBService

stories_bp = Blueprint('stories', __name__, url_prefix='/stories')

@stories_bp.route('/')
def index():
    """Render the stories overview page."""
    try:
        mongodb = current_app.mongodb
        recent_stories = mongodb.get_stories(limit=10)
        return render_template('stories/index.html', stories=recent_stories)
    except Exception as e:
        current_app.logger.error(f"Error fetching stories: {str(e)}")
        return render_template('errors/500.html'), 500

@stories_bp.route('/create', methods=['GET', 'POST'])
def create():
    """Handle story creation."""
    if request.method == 'POST':
        try:
            data = request.get_json()
            mongodb = current_app.mongodb
            story_id = mongodb.create_story(data)
            return jsonify({'story_id': story_id})
        except Exception as e:
            current_app.logger.error(f"Error creating story: {str(e)}")
            return jsonify({'error': 'Internal server error'}), 500
    return render_template('stories/create.html')

@stories_bp.route('/<story_id>')
def view(story_id):
    """Render a specific story."""
    try:
        mongodb = current_app.mongodb
        story = mongodb.get_story(story_id)
        if not story:
            return render_template('errors/404.html'), 404
        return render_template('stories/output.html', story=story)
    except Exception as e:
        current_app.logger.error(f"Error viewing story {story_id}: {str(e)}")
        return render_template('errors/500.html'), 500

@stories_bp.route('/api/stories')
def get_stories():
    """API endpoint to get stories data."""
    try:
        mongodb = current_app.mongodb
        limit = request.args.get('limit', default=10, type=int)
        stories = mongodb.get_stories(limit=limit)
        return jsonify({'stories': stories})
    except Exception as e:
        current_app.logger.error(f"Error fetching stories API: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500 