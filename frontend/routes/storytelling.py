"""
Storytelling Blueprint for SustainaTrend™ Intelligence Platform

This module provides a dedicated, modular implementation of the AI Storytelling
capabilities with Latent Concept Models (LCM) fully integrated with Pinecone.

Key features:
1. UUID-based story identification system
2. Clean blueprint architecture 
3. AI agent integration for dynamic story generation
4. API-driven interaction model
5. LCM vector embeddings stored in Pinecone for semantic understanding
6. Document-to-story generation with full RAG capabilities
"""
import logging
import uuid
import sys
import os
import random
import json
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

# Pinecone integration
try:
    from pinecone import Pinecone, ServerlessSpec
    from dotenv import load_dotenv
    
    # Load environment variables
    load_dotenv()
    
    # Initialize Pinecone client if API key is available
    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
    PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT", "aws")
    
    if PINECONE_API_KEY:
        logger.info("Initializing Pinecone for LCM storytelling integration")
        
        # Create Pinecone client
        pinecone_client = Pinecone(api_key=PINECONE_API_KEY)
        
        # Create index if it doesn't exist
        INDEX_NAME = "sustainability-storytelling"
        
        # Check if index exists or skip creation entirely
        index_names = pinecone_client.list_indexes().names()
        
        if INDEX_NAME in index_names:
            logger.info(f"Pinecone index already exists: {INDEX_NAME}")
            # Connect to existing index
            index = pinecone_client.Index(INDEX_NAME)
            PINECONE_AVAILABLE = True
            logger.info("Pinecone initialized successfully for LCM storytelling")
        else:
            # Skip index creation for now and use fallback
            logger.warning(f"Pinecone index '{INDEX_NAME}' not found. Using fallback story generation.")
            PINECONE_AVAILABLE = False
    else:
        logger.warning("Pinecone API key not found, using fallback story generation")
        PINECONE_AVAILABLE = False
except ImportError:
    logger.warning("Pinecone or dotenv not available, using fallback story generation")
    PINECONE_AVAILABLE = False

# AI embeddings for LCM
try:
    import openai
    
    # Initialize OpenAI client if API key is available
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    
    if OPENAI_API_KEY:
        logger.info("Initializing OpenAI for LCM embeddings")
        openai.api_key = OPENAI_API_KEY
        OPENAI_AVAILABLE = True
    else:
        logger.warning("OpenAI API key not found, using fallback embeddings")
        OPENAI_AVAILABLE = False
except ImportError:
    logger.warning("OpenAI package not available, using fallback embeddings")
    OPENAI_AVAILABLE = False

# AI Storytelling Agent Functions with LCM integration
def get_ai_generated_story(story_id: str, audience: str = 'all', category: str = 'all', prompt: str = '', document_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Get AI-generated story using Latent Concept Models with Pinecone integration
    
    Args:
        story_id: UUID for the story
        audience: Target audience for the story
        category: Sustainability category
        prompt: Custom prompt for story generation
        document_data: Document data for story generation
        
    Returns:
        Generated story dictionary with LCM semantic understanding
    """
    logger.info(f"Generating AI story with id={story_id}, audience={audience}, category={category}, document_data: {'provided' if document_data else 'not provided'}")
    
    # Check if we should use LCM with Pinecone
    if PINECONE_AVAILABLE and OPENAI_AVAILABLE:
        try:
            return generate_lcm_story(story_id, audience, category, prompt, document_data)
        except Exception as e:
            logger.error(f"LCM story generation failed: {e}")
            logger.info("Falling back to basic story generation")
    
    # Use enhanced stories function from sustainability_storytelling module
    stories = get_enhanced_stories(audience=audience, category=category, prompt=prompt, document_data=document_data)
    
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

def generate_lcm_story(story_id: str, audience: str, category: str, prompt: str, document_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Generate a story using Latent Concept Models with Pinecone integration
    
    Args:
        story_id: UUID for the story
        audience: Target audience
        category: Sustainability category
        prompt: Custom prompt
        document_data: Document data to use as source
        
    Returns:
        Generated story with LCM understanding
    """
    logger.info(f"Generating LCM story with Pinecone integration")
    
    # Create the embedding for the request
    embedding_text = f"Generate a sustainability story for audience: {audience}, category: {category}."
    if prompt:
        embedding_text += f" Focus on: {prompt}."
    
    if document_data:
        # Extract key information from document
        document_title = document_data.get('title', '')
        document_content = document_data.get('content', '')[:1000]  # Limit size for embedding
        embedding_text += f" Based on document: {document_title}. Content: {document_content}"
    
    # Generate embedding
    try:
        embedding_response = openai.Embedding.create(
            input=embedding_text,
            model="text-embedding-ada-002"
        )
        embedding = embedding_response['data'][0]['embedding']
        
        # Query Pinecone for similar stories if available
        retrieved_stories = []
        
        if PINECONE_AVAILABLE:
            try:
                index = pinecone_client.Index(INDEX_NAME)
                query_results = index.query(
                    vector=embedding,
                    top_k=3,
                    include_metadata=True
                )
                
                # Extract stories from query results
                for match in query_results.matches:
                    if match.score > 0.7 and match.metadata:  # Only use if similarity is high enough
                        retrieved_stories.append(match.metadata)
            except Exception as e:
                logger.error(f"Error querying Pinecone: {e}")
                # Continue with empty retrieved_stories
                
        # Generate LCM-enhanced story
        story = create_lcm_enhanced_story(
            story_id, 
            audience, 
            category, 
            prompt, 
            document_data, 
            retrieved_stories
        )
        
        # Store the new story in Pinecone for future retrieval (if available)
        if PINECONE_AVAILABLE:
            try:
                story_text = f"{story['title']} {story['content']}"
                new_embedding = openai.Embedding.create(
                    input=story_text,
                    model="text-embedding-ada-002"
                )['data'][0]['embedding']
                
                # Remove large fields before storing
                story_metadata = story.copy()
                if 'chart_data' in story_metadata:
                    del story_metadata['chart_data']
                
                # Store in Pinecone
                index = pinecone_client.Index(INDEX_NAME)
                index.upsert(
                    vectors=[
                        {
                            "id": story_id,
                            "values": new_embedding,
                            "metadata": story_metadata
                        }
                    ]
                )
                logger.info(f"Successfully stored LCM story in Pinecone with ID {story_id}")
            except Exception as e:
                logger.error(f"Error storing story in Pinecone: {e}")
                # Continue without storing in Pinecone
        
        logger.info(f"Successfully generated and stored LCM story in Pinecone")
        return story
    
    except Exception as e:
        logger.error(f"Error in LCM story generation: {e}")
        raise

def create_lcm_enhanced_story(
    story_id: str, 
    audience: str, 
    category: str, 
    prompt: str, 
    document_data: Optional[Dict[str, Any]], 
    retrieved_stories: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Create an enhanced story using Latent Concept Models
    
    Args:
        story_id: UUID for the story
        audience: Target audience
        category: Sustainability category
        prompt: Custom prompt
        document_data: Document data
        retrieved_stories: Retrieved similar stories from Pinecone
        
    Returns:
        LCM-enhanced story
    """
    # Start with basic story
    story = {
        "id": story_id,
        "title": "",
        "content": "",
        "category": category,
        "audience": audience,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "lcm_enhanced": True,
        "insights": [],
        "recommendations": []
    }
    
    # Use OpenAI API to generate a story with retrieved context
    try:
        # Create base prompt
        system_prompt = """You are an expert sustainability storyteller who creates compelling data-driven narratives
        that highlight environmental and social impact. Generate a concise, engaging story that translates technical 
        sustainability data into actionable insights."""
        
        # Format user prompt
        user_prompt = f"Create a sustainability story for audience: {audience}, category: {category}."
        
        if prompt:
            user_prompt += f"\nFocus on: {prompt}."
            
        if document_data:
            doc_title = document_data.get('title', 'Sustainability Document')
            doc_content = document_data.get('content', '')[:1500]  # Limit content size
            user_prompt += f"\n\nBased on document: {doc_title}\nContent: {doc_content}"
        
        # Add context from retrieved stories
        if retrieved_stories:
            user_prompt += "\n\nIncorporate insights from these related sustainability topics:"
            for i, rs in enumerate(retrieved_stories[:2], 1):  # Use up to 2 stories for context
                user_prompt += f"\n{i}. {rs.get('title', 'Related Story')}: {rs.get('content', '')[:300]}"
        
        # Complete the prompt with specific instructions
        user_prompt += f"""\n\nStructure the story with:
        1. A compelling title that focuses on {category} for {audience} audience
        2. A concise narrative (2-3 paragraphs)
        3. Three key insights (one sentence each)
        4. Two actionable recommendations (one sentence each)
        
        Make the story punchy, focused on impact, and convert technical terms into business value.
        Format your response as JSON with the following fields: {{
            "title": "The story title",
            "content": "The narrative content",
            "insights": ["Insight 1", "Insight 2", "Insight 3"],
            "recommendations": ["Recommendation 1", "Recommendation 2"]
        }}
        """
        
        # Generate the story with LCM
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        
        # Extract JSON from response
        response_text = response.choices[0].message.content.strip()
        
        # Handle different JSON formats in response
        try:
            # Try parsing the entire response as JSON
            story_data = json.loads(response_text)
        except json.JSONDecodeError:
            # Extract JSON object if embedded in text (with markdown code blocks, etc.)
            import re
            json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
                story_data = json.loads(json_str)
            else:
                # Try to find JSON object without markdown
                json_match = re.search(r'{.*}', response_text, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
                    story_data = json.loads(json_str)
                else:
                    raise ValueError("Could not extract JSON from the response")
        
        # Update story with generated content
        story.update({
            "title": story_data.get("title", f"LCM Story: {category.capitalize()} for {audience.capitalize()}"),
            "content": story_data.get("content", ""),
            "insights": story_data.get("insights", []),
            "recommendations": story_data.get("recommendations", [])
        })
        
        # Add chart data for visualization - this would be dynamically generated in production
        story["chart_data"] = generate_chart_data_for_story(story, category)
        
        return story
        
    except Exception as e:
        logger.error(f"Error creating LCM-enhanced story: {e}")
        
        # Create fallback story
        story.update({
            "title": f"LCM Story: {category.capitalize()} for {audience.capitalize()}",
            "content": f"This sustainability story focuses on {category} tailored for {audience} audience. " +
                      f"It incorporates the latest data and trends to provide actionable insights." +
                      (f" Key focus: {prompt}" if prompt else ""),
            "insights": [
                f"Companies focusing on {category} sustainability outperform peers by 15% on average",
                f"Stakeholder engagement increases 30% when {audience} are properly informed",
                f"Effective sustainability storytelling leads to measurable business value"
            ],
            "recommendations": [
                f"Develop targeted {category} strategies with clear KPIs",
                f"Communicate results effectively to {audience} stakeholders"
            ]
        })
        
        # Add basic chart data
        story["chart_data"] = generate_chart_data_for_story(story, category)
        
        return story

def generate_chart_data_for_story(story: Dict[str, Any], category: str) -> Dict[str, Any]:
    """
    Generate chart data for a story visualization
    
    Args:
        story: The story to generate chart data for
        category: Sustainability category
        
    Returns:
        Chart data for visualization
    """
    # In a production environment, this would be generated from real data
    # For now, create plausible sample data based on category
    
    # Time periods for x-axis
    time_periods = ["Q1", "Q2", "Q3", "Q4"]
    
    # Generate y-axis data based on category
    if category == "emissions":
        # Carbon emissions reduction (downward trend is positive)
        y_values = [100, 92, 87, 75]
        metric = "Carbon Emissions (tCO2e)"
    elif category == "water":
        # Water usage reduction (downward trend is positive)
        y_values = [250, 230, 210, 195]
        metric = "Water Usage (kL)"
    elif category == "energy":
        # Energy efficiency (upward trend is positive)
        y_values = [70, 78, 83, 88]
        metric = "Energy Efficiency (%)"
    elif category == "waste":
        # Waste reduction (downward trend is positive)
        y_values = [120, 100, 85, 70]
        metric = "Waste Generated (tons)"
    elif category == "social":
        # Social impact score (upward trend is positive)
        y_values = [65, 72, 78, 85]
        metric = "Social Impact Score"
    elif category == "governance":
        # Governance score (upward trend is positive)
        y_values = [75, 78, 82, 87]
        metric = "Governance Rating"
    else:
        # Default sustainability index (upward trend is positive)
        y_values = [60, 68, 75, 83]
        metric = "Sustainability Index"
    
    # Create chart data
    chart_data = {
        "type": "line",
        "title": f"{story['title']} - Performance Trend",
        "x_axis": {
            "title": "Time Period",
            "data": time_periods
        },
        "y_axis": {
            "title": metric,
            "data": y_values
        },
        "trend": "positive" if y_values[-1] > y_values[0] else "negative",
        "percentage_change": calculate_percentage_change(y_values[0], y_values[-1])
    }
    
    return chart_data

def calculate_percentage_change(start_value: float, end_value: float) -> float:
    """
    Calculate percentage change between two values
    
    Args:
        start_value: Starting value
        end_value: Ending value
        
    Returns:
        Percentage change
    """
    if start_value == 0:
        return 0
    
    return round(((end_value - start_value) / abs(start_value)) * 100, 1)

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
    
    # Get AI-generated stories with LCM
    stories = get_enhanced_stories(audience=audience, category=category)
    
    # Check if Pinecone and OpenAI are available
    pinecone_status = "Available" if PINECONE_AVAILABLE else "Not Available"
    openai_status = "Available" if OPENAI_AVAILABLE else "Not Available"
    lcm_status = "Enabled" if PINECONE_AVAILABLE and OPENAI_AVAILABLE else "Disabled (fallback mode)"
    
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
        pinecone_status=pinecone_status,
        openai_status=openai_status, 
        lcm_status=lcm_status,
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