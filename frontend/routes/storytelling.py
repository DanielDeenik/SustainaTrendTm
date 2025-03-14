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
from frontend.sustainability_storytelling import get_enhanced_stories, get_data_driven_stories
from frontend.navigation_config import get_context_for_template

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
    # Use our improved, flexible Pinecone initialization logic
    from frontend.initialize_pinecone import (
        initialize_pinecone, 
        get_index_name, 
        is_pinecone_available,
        test_pinecone_connection
    )
    
    logger.info("Initializing Pinecone for LCM storytelling integration")
    
    # Initialize Pinecone using our robust initialization function
    if initialize_pinecone():
        PINECONE_AVAILABLE = is_pinecone_available()
        INDEX_NAME = get_index_name()
        logger.info(f"Connected to Pinecone index: {INDEX_NAME}")
        
        # Verify the connection works
        if test_pinecone_connection():
            logger.info("Successfully verified Pinecone connection for LCM storytelling")
        else:
            logger.warning("Pinecone connection test failed. Using fallback story generation.")
            PINECONE_AVAILABLE = False
    else:
        # If initialization failed, use fallback
        logger.warning(f"Pinecone index initialization failed. Using fallback story generation.")
        PINECONE_AVAILABLE = False
        INDEX_NAME = "sustainability-storytelling"  # Default name for reference
except Exception as e:
    logger.error(f"Error connecting to Pinecone: {e}")
    logger.warning("Using fallback story generation due to Pinecone connection error.")
    PINECONE_AVAILABLE = False
    INDEX_NAME = "sustainability-storytelling"  # Default name for reference

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
    
    # Generate embedding with OpenAI API v1.0 compatibility
    try:
        # Check which OpenAI API version we're using
        if hasattr(openai, 'Embedding'):
            # Using older openai < 1.0.0
            embedding_response = openai.Embedding.create(
                input=embedding_text,
                model="text-embedding-ada-002"
            )
            embedding = embedding_response['data'][0]['embedding']
        else:
            # Using newer openai >= 1.0.0
            client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            embedding_response = client.embeddings.create(
                input=embedding_text,
                model="text-embedding-ada-002"
            )
            embedding = embedding_response.data[0].embedding
        
        # Query Pinecone for similar stories if available
        retrieved_stories = []
        
        if PINECONE_AVAILABLE:
            try:
                from pinecone import Pinecone  # Importing here to avoid issues if not available
                
                # Create Pinecone client
                pinecone_client = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
                
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
                from pinecone import Pinecone  # Importing here to avoid issues if not available
                
                # Create Pinecone client
                pinecone_client = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
                
                story_text = f"{story['title']} {story['content']}"
                
                # Check which OpenAI API version we're using
                if hasattr(openai, 'Embedding'):
                    # Using older openai < 1.0.0
                    embedding_response = openai.Embedding.create(
                        input=story_text,
                        model="text-embedding-ada-002"
                    )
                    new_embedding = embedding_response['data'][0]['embedding']
                else:
                    # Using newer openai >= 1.0.0
                    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
                    embedding_response = client.embeddings.create(
                        input=story_text,
                        model="text-embedding-ada-002"
                    )
                    new_embedding = embedding_response.data[0].embedding
                
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
        
        # Generate the story with LCM using OpenAI API v1.0 compatibility
        if hasattr(openai, 'ChatCompletion'):
            # Using older openai < 1.0.0
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
        else:
            # Using newer openai >= 1.0.0
            client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            response = client.chat.completions.create(
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
        y_values = [85, 75, 68, 55]
        metric = "Waste Production (tons)"
    elif category == "social":
        # Social impact score (upward trend is positive)
        y_values = [65, 72, 78, 85]
        metric = "Social Impact Score"
    elif category == "governance":
        # Governance score (upward trend is positive)
        y_values = [70, 75, 82, 88]
        metric = "Governance Score"
    else:
        # Generic sustainability score (upward trend is positive)
        y_values = [60, 68, 75, 82]
        metric = "Sustainability Score"
    
    # Create chart data in format suitable for recharts
    chart_data = {
        "type": "line",  # Default chart type
        "title": f"{metric} Trend",
        "xAxis": {"dataKey": "quarter", "label": "Quarter"},
        "yAxis": {"label": metric},
        "data": [{"quarter": q, "value": v} for q, v in zip(time_periods, y_values)]
    }
    
    return chart_data

def get_story_by_id(story_id: str) -> Optional[Dict[str, Any]]:
    """
    Get a story by its ID, either from Pinecone or generated on-demand
    
    Args:
        story_id: UUID of the story to retrieve
        
    Returns:
        Story dictionary or None if not found
    """
    # Try to retrieve from Pinecone first if available
    if PINECONE_AVAILABLE and OPENAI_AVAILABLE:
        try:
            from pinecone import Pinecone
            
            # Create Pinecone client
            pinecone_client = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
            
            # Query Pinecone for the story by ID
            try:
                index = pinecone_client.Index(INDEX_NAME)
                result = index.fetch(ids=[story_id])
                
                if result.vectors and story_id in result.vectors:
                    # Extract metadata (the story content)
                    story = result.vectors[story_id].metadata
                    
                    # Ensure the story has an ID
                    if story:
                        story['id'] = story_id
                        
                        # Generate chart data if not present
                        if 'chart_data' not in story and 'category' in story:
                            story['chart_data'] = generate_chart_data_for_story(story, story['category'])
                            
                        return story
            except Exception as e:
                logger.error(f"Error fetching story from Pinecone: {e}")
        except Exception as e:
            logger.error(f"Error connecting to Pinecone for story retrieval: {e}")
    
    # Generate a new story if we couldn't find it
    logger.info(f"Story {story_id} not found in Pinecone, generating a new one")
    
    # Parse story ID components if it's in the expected format
    try:
        # Our UUIDs might encode metadata like audience-category-timestamp, 
        # but we'll use defaults if we can't parse
        parts = story_id.split('-')
        if len(parts) >= 3:
            audience = parts[0]
            category = parts[1]
        else:
            audience = 'all'
            category = 'emissions'
    except:
        audience = 'all'
        category = 'emissions'
    
    return get_ai_generated_story(story_id, audience, category)

# Blueprint routes
@storytelling_bp.route('/')
@storytelling_bp.route('/<category>')
def storytelling_home(category='all'):
    """
    Storytelling home page
    
    Args:
        category: Category filter for stories (default: 'all')
    
    Returns:
        Rendered template with storytelling UI
    """
    # Import directly to ensure we're using the latest version
    try:
        from frontend.story_operations import PINECONE_AVAILABLE, OPENAI_AVAILABLE
        pinecone_status = "Available" if PINECONE_AVAILABLE else "Unavailable"
        openai_status = "Available" if OPENAI_AVAILABLE else "Unavailable"
        lcm_status = "Enabled" if PINECONE_AVAILABLE and OPENAI_AVAILABLE else "Disabled"
    except ImportError:
        logger.warning("Story operations module not available, using default values")
        PINECONE_AVAILABLE = False
        OPENAI_AVAILABLE = False
        pinecone_status = "Unavailable"
        openai_status = "Unavailable"
        lcm_status = "Disabled"
    
    # Get stories from the base module or generate them with category filter
    logger.info(f"Generating enhanced stories for audience: all, category: {category if category != 'all' else None}, prompt: None, document_data: not provided")
    
    # Convert category to None if 'all' is selected
    category_filter = None if category == 'all' else category
    
    try:
        # Use imported function from sustainability_storytelling
        stories = get_enhanced_stories(audience='all', category=category_filter)
        logger.info(f"Generated {len(stories)} enhanced stories")
    except Exception as e:
        logger.error(f"Error generating enhanced stories: {e}")
        stories = []
    
    # If no stories found and not specifically filtered, generate a default story
    if not stories:
        logger.info("No matching stories found, generating a default story")
        # Generate a default story with a unique ID
        story_id = str(uuid.uuid4())
        default_story = {
            "id": story_id,
            "title": "Welcome to Sustainability Storytelling",
            "content": "This is your central hub for creating data-driven sustainability narratives. Generate your first story by clicking the 'Create New Story' button above.",
            "category": "general" if category == 'all' else category,
            "audience": "all",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "recommendations": [
                "Try creating a story with a specific sustainability focus like emissions or water usage.",
                "Explore different audience types for targeted storytelling."
            ]
        }
        stories = [default_story]
        logger.info(f"Generated default story with ID: {story_id}")
        
        # Try to save the default story for future use
        try:
            from frontend.story_operations import save_new_story
            save_new_story(default_story)
            logger.info(f"Saved default story with ID: {story_id}")
        except Exception as e:
            logger.warning(f"Could not save default story: {e}")
    
    # Pass to template with navigation context
    context = get_context_for_template()
    context.update({
        'page_title': 'Sustainability Storytelling',
        'stories': stories,
        'active_page': 'storytelling',
        'selected_category': category,
        'storytelling_available': STORYTELLING_AVAILABLE,
        'pinecone_status': pinecone_status,
        'openai_status': openai_status,
        'lcm_status': lcm_status
    })
    
    try:
        logger.info(f"Attempting to render template: {DEFAULT_TEMPLATE} with context: stories={len(stories)}, page_title={context['page_title']}")
        return render_template(DEFAULT_TEMPLATE, **context)
    except Exception as e:
        logger.error(f"Error rendering storytelling template: {e}")
        # Try with a simple fallback template
        fallback_template = "storytelling/main.html"
        logger.info(f"Trying fallback template: {fallback_template}")
        try:
            return render_template(fallback_template, **context)
        except Exception as e2:
            logger.error(f"Error rendering fallback template: {e2}")
            # Try another fallback
            try:
                logger.info("Trying direct template: sustainability_storytelling_dark.html")
                return render_template("sustainability_storytelling_dark.html", **context)
            except Exception as e3:
                logger.error(f"Error rendering direct template: {e3}")
                # Last resort fallback - render basic HTML
                html_content = f"""
                <html>
                <head><title>Sustainability Storytelling</title></head>
                <body>
                    <h1>Sustainability Storytelling</h1>
                    <p>Stories count: {len(stories)}</p>
                    <a href="{url_for('storytelling.create_story')}">Create New Story</a>
                    <hr>
                    <h2>Debug Information</h2>
                    <p>ERROR: Template rendering failed</p>
                    <p>Original error: {str(e)}</p>
                    <p>Fallback error: {str(e2)}</p>
                    <p>Direct template error: {str(e3)}</p>
                </body>
                </html>
                """
                return html_content

@storytelling_bp.route('/api/stories', methods=['GET'])
def api_get_stories():
    """
    API endpoint to get stories
    
    Returns:
        JSON response with stories
    """
    # Parse query parameters
    audience = request.args.get('audience', 'all')
    category = request.args.get('category', 'all')
    limit = int(request.args.get('limit', 5))
    
    # Get stories from the base module
    stories = get_enhanced_stories(audience=audience, category=category)
    
    # Limit the number of stories
    stories = stories[:limit]
    
    return jsonify({
        'status': 'success',
        'stories': stories
    })

@storytelling_bp.route('/api/story/<story_id>', methods=['GET'])
def api_get_story(story_id):
    """
    API endpoint to get a specific story by ID
    
    Args:
        story_id: UUID of the story
        
    Returns:
        JSON response with the story
    """
    # Import directly to ensure we're using the latest version
    from frontend.story_operations import get_story_by_id
    
    # Get story by ID
    story = get_story_by_id(story_id)
    
    if story:
        return jsonify({
            'status': 'success',
            'story': story
        })
    else:
        return jsonify({
            'status': 'error',
            'message': f'Story with ID {story_id} not found'
        }), 404

@storytelling_bp.route('/api/stories/generate', methods=['POST'])
@storytelling_bp.route('/api/generate-story', methods=['POST'])
def api_generate_story():
    """
    API endpoint to generate a new story
    
    Returns:
        JSON response with the generated story
    """
    # Import directly to ensure we're using the latest version
    from frontend.story_operations import save_new_story
    
    data = request.json or {}
    
    # Parse parameters
    audience = data.get('audience', 'all')
    category = data.get('category', 'all')
    prompt = data.get('prompt', '')
    document_data = data.get('document_data')
    
    # Generate a unique ID for the story
    story_id = f"{audience}-{category}-{uuid.uuid4()}"
    
    # Generate the story using our local function
    story = get_ai_generated_story(story_id, audience, category, prompt, document_data)
    
    # Save the generated story using our story_operations module
    if story and 'id' in story:
        save_new_story(story)
    
    return jsonify({
        'status': 'success',
        'story': story
    })

@storytelling_bp.route('/create')
def create_story():
    """
    Create a new story form page
    
    Returns:
        Rendered template with story creation form
    """
    # Import directly to ensure we're using the latest version
    from frontend.story_operations import PINECONE_AVAILABLE, OPENAI_AVAILABLE
    
    # Pass to template with navigation context
    context = get_context_for_template()
    context.update({
        'page_title': 'Create Sustainability Story',
        'active_page': 'storytelling',
        'storytelling_available': STORYTELLING_AVAILABLE,
        'lcm_available': PINECONE_AVAILABLE and OPENAI_AVAILABLE
    })
    
    return render_template('strategy/create_story.html', **context)

@storytelling_bp.route('/story/<story_id>')
def view_story(story_id):
    """
    View a specific story
    
    Args:
        story_id: UUID of the story
        
    Returns:
        Rendered template with the story
    """
    # Import directly to ensure we're using the latest version
    from frontend.story_operations import get_story_by_id
    from frontend.story_operations import PINECONE_AVAILABLE, OPENAI_AVAILABLE
    
    # Get story by ID
    story = get_story_by_id(story_id)
    
    if story:
        # Pass to template with navigation context
        context = get_context_for_template()
        context.update({
            'page_title': story.get('title', 'Sustainability Story'),
            'story': story,
            'active_page': 'storytelling',
            'storytelling_available': STORYTELLING_AVAILABLE,
            'lcm_available': PINECONE_AVAILABLE and OPENAI_AVAILABLE
        })
        
        return render_template('strategy/story_detail.html', **context)
    else:
        return render_template('error.html', error=f'Story with ID {story_id} not found'), 404

@storytelling_bp.route('/api/story/<story_id>/view', methods=['POST'])
def api_record_story_view(story_id):
    """
    API endpoint to record a view for a story
    
    Args:
        story_id: ID of the story
        
    Returns:
        JSON with success status
    """
    try:
        # Import directly to ensure we're using the latest version
        from frontend.story_operations import get_story_by_id, update_story
        
        # Get the story
        story = get_story_by_id(story_id)
        
        if not story:
            return jsonify({
                'success': False,
                'error': 'Story not found'
            }), 404
        
        # Increment view count (simple in-memory implementation)
        if 'views' not in story:
            story['views'] = 0
        story['views'] += 1
        
        # Update the story in the storage
        update_story(story_id, story)
        
        return jsonify({
            'success': True,
            'views': story['views']
        })
    except Exception as e:
        logger.error(f"Error recording story view: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@storytelling_bp.route('/api/story/<story_id>/delete', methods=['POST'])
def api_delete_story(story_id):
    """
    API endpoint to delete a story
    
    Args:
        story_id: ID of the story
        
    Returns:
        JSON with success status
    """
    try:
        # Import directly to ensure we're using the latest version
        from frontend.story_operations import get_story_by_id, delete_story
        
        # Check if the story exists first
        story = get_story_by_id(story_id)
        
        if not story:
            return jsonify({
                'success': False,
                'error': 'Story not found'
            }), 404
        
        # Delete the story
        success = delete_story(story_id)
        
        return jsonify({
            'success': success,
            'message': 'Story deleted successfully' if success else 'Failed to delete story'
        })
    except Exception as e:
        logger.error(f"Error deleting story: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@storytelling_bp.route('/api/story/<story_id>/export/pdf')
def api_export_story_pdf(story_id):
    """
    Export a story as PDF
    
    Args:
        story_id: ID of the story
        
    Returns:
        PDF file download
    """
    try:
        # Import directly to ensure we're using the latest version
        from frontend.story_operations import get_story_by_id
        from flask import make_response
        
        # Get the story
        story = get_story_by_id(story_id)
        
        if not story:
            return render_template('error.html', error='Story not found'), 404
        
        # Generate PDF
        from fpdf import FPDF
        
        # Create PDF instance
        pdf = FPDF()
        pdf.add_page()
        
        # Set font
        pdf.set_font("Arial", "B", 16)
        
        # Title
        pdf.cell(0, 10, story.get('title', 'Sustainability Story'), 0, 1, 'C')
        
        # Metadata
        pdf.set_font("Arial", "I", 10)
        pdf.cell(0, 10, f"Category: {story.get('category', 'General')}", 0, 1)
        pdf.cell(0, 10, f"Audience: {story.get('audience', 'All')}", 0, 1)
        if 'timestamp' in story:
            pdf.cell(0, 10, f"Created: {story.get('timestamp')}", 0, 1)
        
        # Content
        pdf.set_font("Arial", "", 12)
        pdf.ln(10)
        
        # Split content into paragraphs and add to PDF
        content = story.get('content', '')
        paragraphs = content.split('\n\n') if '\n\n' in content else [content]
        
        for paragraph in paragraphs:
            pdf.multi_cell(0, 10, paragraph)
            pdf.ln(5)
        
        # Recommendations
        if 'recommendations' in story and story['recommendations']:
            pdf.ln(10)
            pdf.set_font("Arial", "B", 14)
            pdf.cell(0, 10, "Recommendations", 0, 1)
            pdf.set_font("Arial", "", 12)
            
            for recommendation in story['recommendations']:
                pdf.cell(0, 10, "• " + recommendation, 0, 1)
        
        # Footer
        pdf.ln(15)
        pdf.set_font("Arial", "I", 8)
        pdf.cell(0, 10, "Generated by SustainaTrend™ Intelligence Platform", 0, 1, 'C')
        
        # Create response
        pdf_output = pdf.output(dest='S')
        if isinstance(pdf_output, str):
            pdf_bytes = pdf_output.encode('latin-1')
        else:
            pdf_bytes = pdf_output
        
        response = make_response(pdf_bytes)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename=sustainability_story_{story_id}.pdf'
        
        return response
    except Exception as e:
        logger.error(f"Error exporting story as PDF: {str(e)}")
        return render_template('error.html', error=f'Error exporting story: {str(e)}'), 500