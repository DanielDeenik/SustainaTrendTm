"""
Storytelling API for SustainaTrend™ Intelligence Platform

This module provides the API endpoints for data-driven storytelling
based on Gartner's three-part narrative structure:
- Context: Why this matters now
- Narrative: What is happening in the data
- Visual: AI-generated chart recommendation
"""

import logging
import os
import sys
import json
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
from flask import Flask, jsonify, request

# Import storytelling service
try:
    from services.storytelling_service import create_story_card, get_sample_story_cards
except ImportError:
    # Create a stub for the import
    def create_story_card(*args, **kwargs):
        return {
            "error": "Storytelling service not available",
            "message": "The storytelling service module could not be imported"
        }
    
    def get_sample_story_cards(count=3):
        return []

# Configure logging
logger = logging.getLogger(__name__)

def get_sustainability_metrics():
    """Get sustainability metrics data from the backend"""
    try:
        # Try to get metrics from service
        from services.simple_mock_service import SimpleMockService
        mock_service = SimpleMockService()
        return mock_service.get_metrics(limit=30)
    except ImportError:
        logger.warning("SimpleMockService not available for metrics")
        # Return an empty list if service is not available
        return []

def get_mock_stories():
    """Get mock storytelling data"""
    try:
        # Try to get stories from service
        from services.simple_mock_service import SimpleMockService
        mock_service = SimpleMockService()
        return mock_service.get_stories(limit=10)
    except ImportError:
        logger.warning("SimpleMockService not available for stories")
        # Return an empty list if service is not available
        return []

def register_routes(app):
    """
    Register storytelling API routes
    
    Args:
        app: Flask application
    """
    @app.route('/api/storytelling', methods=['POST'])
    def api_storytelling():
        """
        API endpoint for AI storytelling generation with Gartner-inspired methodology
        
        Generates data-driven storytelling following Gartner's three-part narrative structure:
        - Context: Why this matters now
        - Narrative: What is happening in the data
        - Visual: AI-generated chart recommendation
        
        Each story includes:
        1. Headline (15 words max)
        2. Narrative summary (3-5 sentences)
        3. AI chart recommendation
        4. Context (regulatory/framework connections)
        5. Recommended actions
        
        Request parameters:
        - metric: Target metric for storytelling (e.g., 'Carbon Emissions')
        - time_period: Timeframe for analysis (e.g., 'Last Quarter')
        - narrative_focus: Focus type ('Performance Analysis', 'Risk Assessment', 'CSRD/ESG Compliance')
        - audience: Target stakeholder ('Board', 'Sustainability Team', 'Investors')
        - context: Additional context
        - data_source: Source of data ('metrics', 'trends', 'documents', 'external')
        - chart_type: (Optional) Specific chart type or 'auto' for AI-selected
        """
        logger.info("API storytelling endpoint accessed")
        
        try:
            # Get and validate request data
            data = request.json or {}
            
            # Get parameters for storytelling
            metric = data.get('metric', 'Carbon Emissions')
            time_period = data.get('time_period', 'Last Quarter')
            narrative_focus = data.get('narrative_focus', 'Performance Analysis')
            audience = data.get('audience', 'Board')
            context = data.get('context', '')
            source_type = data.get('data_source', 'metrics')
            chart_type = data.get('chart_type', 'auto')
            
            logger.info(f"Generating story for metric: {metric}, focus: {narrative_focus}, audience: {audience}")
            
            # Get relevant data based on the source type
            source_data = {}
            
            if source_type == 'metrics':
                # Get metrics data
                metrics_data = get_sustainability_metrics()
                
                if isinstance(metrics_data, dict) and 'metrics' in metrics_data:
                    all_metrics = metrics_data['metrics']
                else:
                    all_metrics = metrics_data if isinstance(metrics_data, list) else []
                
                # Filter metrics relevant to the requested metric
                relevant_metrics = [
                    m for m in all_metrics 
                    if metric.lower() in m.get('name', '').lower() 
                    or metric.lower() in m.get('category', '').lower()
                ]
                
                source_data['metrics'] = relevant_metrics or all_metrics[:5]  # Use top 5 if none match
                
            elif source_type == 'trends':
                # Get trend data
                try:
                    from mongo_trends import get_trends
                    trends = get_trends(limit=10)
                except ImportError:
                    try:
                        from services.simple_mock_service import SimpleMockService
                        mock_service = SimpleMockService()
                        trends = mock_service.get_trends(limit=10)
                    except ImportError:
                        trends = []
                
                source_data['trends'] = trends
                
            elif source_type == 'documents':
                # Document-based storytelling would connect to the document processor
                try:
                    from document_processor import DocumentProcessor
                    doc_processor = DocumentProcessor()
                    
                    # In a real implementation, this would process actual documents
                    source_data['documents'] = [{
                        'title': 'Sustainability Report',
                        'summary': 'The report covers various sustainability metrics and initiatives.',
                        'kpis': [{'name': 'Carbon Emissions', 'value': '250 tons', 'change': '-5%'}]
                    }]
                except ImportError:
                    logger.warning("Document processor not available")
                    source_data['documents'] = []
                
            elif source_type == 'external':
                # This would integrate with external APIs for data
                source_data['external'] = [{
                    'source': 'Industry Database',
                    'data': [{'name': metric, 'average': 'industry_average'}]
                }]
            
            # Get stories for context
            try:
                from mongo_stories import get_stories
                stories = get_stories(limit=10)
            except ImportError:
                stories = get_mock_stories() or []
            
            # Create a story based on audience type
            story_card = create_story_card(
                metric=metric,
                time_period=time_period,
                narrative_focus=narrative_focus,
                audience=audience,
                context=context,
                chart_type=chart_type,
                source_data=source_data,
                stories=stories
            )
            
            return jsonify(story_card)
            
        except Exception as e:
            logger.error(f"Error generating storytelling content: {str(e)}")
            return jsonify({
                "error": "Error generating storytelling content",
                "status": "error",
                "message": str(e)
            }), 500
    
    @app.route('/api/storytelling/templates', methods=['GET'])
    def api_storytelling_templates():
        """API endpoint for getting storytelling templates"""
        logger.info("API storytelling templates endpoint accessed")
        
        try:
            # Get templates based on audience
            templates = {
                "board": {
                    "title": "Board-Level Narratives",
                    "description": "High-level risk, opportunity, strategic next steps",
                    "prompt_example": "Generate a board-level CSRD story from our current data, focusing on top 3 risks and recommendations."
                },
                "sustainability_team": {
                    "title": "Sustainability Team Insights",
                    "description": "Root causes, detailed action plans, implementation metrics",
                    "prompt_example": "Create a sustainability team analysis of our current emissions trend, focusing on root cause and tactical improvements."
                },
                "investors": {
                    "title": "Investor-Focused Storytelling",
                    "description": "Risk analysis, peer comparison, compliance status, ROI metrics",
                    "prompt_example": "Present our water conservation initiatives as an investor narrative highlighting competitive advantage and risk mitigation."
                }
            }
            
            return jsonify(templates)
            
        except Exception as e:
            logger.error(f"Error retrieving storytelling templates: {str(e)}")
            return jsonify({
                "error": "Error retrieving storytelling templates",
                "message": str(e)
            }), 500
    
    @app.route('/api/storytelling/samples', methods=['GET'])
    def api_storytelling_samples():
        """API endpoint for getting sample story cards"""
        logger.info("API storytelling samples endpoint accessed")
        
        try:
            # Get count parameter
            count = request.args.get('count', 3, type=int)
            
            # Get sample story cards
            samples = get_sample_story_cards(count)
            
            return jsonify({
                "samples": samples,
                "count": len(samples)
            })
            
        except Exception as e:
            logger.error(f"Error generating sample story cards: {str(e)}")
            return jsonify({
                "error": "Error generating sample story cards",
                "message": str(e)
            }), 500

    logger.info("Storytelling API routes registered")
    return app