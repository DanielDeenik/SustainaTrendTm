"""
Streamlined Routes Module for SustainaTrend™ Intelligence Platform

This module provides a clean, minimal structure for all routes in the application,
focusing on AI-driven storytelling with minimal UI and clear data visualization.

Routes include:
- Home page
- Dashboard for sustainability metrics
- Document upload and analysis for sustainability reports
- AI-powered querying of sustainability documents
"""

import os
import time
import json
import uuid
import logging
import random
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict

from flask import (
    render_template, jsonify, request, redirect, 
    url_for, flash, current_app, Blueprint, 
    send_from_directory, Response, session, abort
)
from werkzeug.utils import secure_filename
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Import navigation configuration
try:
    from navigation_config import get_context_for_template
except ImportError:
    # Fallback if navigation_config is not available
    def get_context_for_template():
        """
        Fallback function for navigation context
        """
        return {
            "nav_sections": [],
            "user_menu": []
        }

# Configure logging
logger = logging.getLogger(__name__)

def get_enhanced_stories(audience='all', category='all'):
    """Fallback function for getting enhanced stories"""
    logger.warning("Using fallback get_enhanced_stories function")
    return []

def register_routes(app):
    """
    Register all routes for the SustainaTrend™ Intelligence Platform
    
    Args:
        app: Flask application
    """
    # Ensure the upload directory exists
    upload_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    os.makedirs(upload_dir, exist_ok=True)
    
    # Configure API endpoint
    api_url = os.environ.get('API_URL', 'http://localhost:8000')
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('flask_log.txt')
        ]
    )
    
    @app.route('/')
    def home():
        """Home AI Trends Feed - Entry point with AI-curated sustainability trends"""
        logger.info("Home route accessed")
        
        try:
            # Get navigation context
            nav_context = get_context_for_template()
            
            # Try to get MongoDB stories
            try:
                from mongo_stories import get_stories
                stories = get_stories(limit=4)
                logger.info(f"Retrieved {len(stories)} stories from MongoDB")
            except Exception as e:
                logger.warning(f"Failed to get stories from MongoDB: {e}")
                stories = []
            
            # Get mock stories as fallback if needed
            if not stories:
                stories = [
                    {
                        "title": "Carbon Neutrality Milestone Reached",
                        "content": "Major progress in carbon reduction initiatives has led to a significant milestone. Several key industries have shown remarkable improvement in their sustainability metrics.",
                        "category": "Climate Action",
                        "tags": ["carbon neutral", "industry leaders"],
                        "image_url": "https://source.unsplash.com/featured/?sustainability,carbon",
                        "created_at": datetime.now() - timedelta(days=2)
                    },
                    {
                        "title": "Renewable Energy Adoption Accelerates",
                        "content": "Global adoption of renewable energy sources has accelerated beyond expectations. Solar and wind installations have reached record levels.",
                        "category": "Renewable Energy",
                        "tags": ["solar", "wind energy"],
                        "image_url": "https://source.unsplash.com/featured/?sustainability,solar",
                        "created_at": datetime.now() - timedelta(days=5)
                    },
                    {
                        "title": "Sustainable Supply Chain Innovations",
                        "content": "New technologies are transforming supply chain sustainability. Companies are finding innovative ways to reduce their environmental footprint.",
                        "category": "Supply Chain",
                        "tags": ["innovation", "supply chain"],
                        "image_url": "https://source.unsplash.com/featured/?sustainability,supply",
                        "created_at": datetime.now() - timedelta(days=7)
                    },
                    {
                        "title": "Circular Economy Solutions Gain Traction",
                        "content": "Circular economy principles are being adopted by more industries. Waste reduction and resource reuse are becoming standard practices.",
                        "category": "Circular Economy",
                        "tags": ["waste reduction", "resource efficiency"],
                        "image_url": "https://source.unsplash.com/featured/?sustainability,circular",
                        "created_at": datetime.now() - timedelta(days=10)
                    }
                ]
                logger.info("Using fallback mock stories")
            
            # Try to get MongoDB trends
            try:
                from mongo_trends import get_trends
                trends = get_trends(limit=5)
                logger.info(f"Retrieved {len(trends)} trends from MongoDB")
            except Exception as e:
                logger.warning(f"Failed to get trends from MongoDB: {e}")
                trends = []
            
            # Get mock trends as fallback if needed
            if not trends:
                trends = [
                    {
                        "name": "Carbon Footprint Reduction",
                        "category": "Climate Action",
                        "virality_score": 87,
                        "momentum": "increasing",
                        "created_at": datetime.now() - timedelta(days=3)
                    },
                    {
                        "name": "ESG Reporting Standards",
                        "category": "Governance",
                        "virality_score": 92,
                        "momentum": "increasing",
                        "created_at": datetime.now() - timedelta(days=4)
                    },
                    {
                        "name": "Sustainable Supply Chains",
                        "category": "Supply Chain",
                        "virality_score": 78,
                        "momentum": "stable",
                        "created_at": datetime.now() - timedelta(days=6)
                    },
                    {
                        "name": "Circular Economy Innovation",
                        "category": "Resource Efficiency",
                        "virality_score": 83,
                        "momentum": "increasing",
                        "created_at": datetime.now() - timedelta(days=8)
                    },
                    {
                        "name": "Green Building Certification",
                        "category": "Real Estate",
                        "virality_score": 75,
                        "momentum": "stable",
                        "created_at": datetime.now() - timedelta(days=10)
                    }
                ]
                logger.info("Using fallback mock trends")
                
            # Format stories for the template
            formatted_stories = []
            for story in stories:
                # Ensure created_at is a datetime
                if isinstance(story.get('created_at'), str):
                    try:
                        story['created_at'] = datetime.fromisoformat(story['created_at'])
                    except (ValueError, TypeError):
                        story['created_at'] = datetime.now() - timedelta(days=random.randint(1, 10))
                elif not isinstance(story.get('created_at'), datetime):
                    story['created_at'] = datetime.now() - timedelta(days=random.randint(1, 10))
                
                # Format date for display
                story['formatted_date'] = story['created_at'].strftime('%b %d, %Y')
                formatted_stories.append(story)
            
            return render_template(
                'home.html',
                stories=formatted_stories,
                trends=trends,
                nav_sections=nav_context["nav_sections"],
                user_menu=nav_context["user_menu"],
                active_nav="home"
            )
        except Exception as e:
            logger.error(f"Error in home route: {e}")
            return render_template('error.html', error=str(e))
    
    @app.route('/dashboard')
    def dashboard():
        """Unified dashboard page combining sustainability metrics and key indicators"""
        logger.info("Dashboard route accessed")
        
        # Get a mock service instance for data
        try:
            from services.simple_mock_service import MockDataService
            data_service = MockDataService()
            metrics = data_service.get_sustainability_metrics()
            logger.info(f"Retrieved {len(metrics)} metrics from mock service")
        except Exception as e:
            logger.error(f"Failed to get metrics from mock service: {e}")
            metrics = []
        
        # Try to get MongoDB metrics as an alternative
        if not metrics:
            try:
                from mongo_metrics import get_metrics
                metrics = get_metrics(limit=20)
                logger.info(f"Retrieved {len(metrics)} metrics from MongoDB")
            except Exception as e:
                logger.warning(f"Failed to get metrics from MongoDB: {e}")
                metrics = []
        
        # Generate mock metrics as a last resort
        if not metrics:
            # Generate mock metrics data for demonstration
            categories = ["Carbon Emissions", "Energy Usage", "Water Usage", "Waste Management"]
            metrics = []
            
            for i in range(20):
                category = categories[i % len(categories)]
                metrics.append({
                    "id": str(i),
                    "name": f"{category} Metric {i+1}",
                    "category": category,
                    "value": random.uniform(50, 500),
                    "unit": "tons" if category == "Carbon Emissions" else 
                            "kWh" if category == "Energy Usage" else
                            "gallons" if category == "Water Usage" else
                            "kg",
                    "trend": random.choice(["increasing", "decreasing", "stable"]),
                    "date": datetime.now() - timedelta(days=i % 30)
                })
            logger.info("Using fallback generated metrics")
        
        # Get navigation context
        nav_context = get_context_for_template()
        
        # Group metrics by category
        metrics_by_category = defaultdict(list)
        for metric in metrics:
            metrics_by_category[metric["category"]].append(metric)
        
        return render_template(
            'dashboard.html',
            metrics=metrics,
            metrics_by_category=dict(metrics_by_category),
            categories=list(metrics_by_category.keys()),
            nav_sections=nav_context["nav_sections"],
            user_menu=nav_context["user_menu"],
            active_nav="dashboard"
        )
    
    @app.route('/risk-tracker')
    def risk_tracker():
        """Risk Tracker - Real-time sustainability risk monitoring dashboard"""
        # Get navigation context
        nav_context = get_context_for_template()
        
        # Generate mock risk data for demonstration
        risks = [
            {
                "id": "R001",
                "name": "Carbon Emissions Excess",
                "category": "Environmental",
                "level": "High",
                "impact": "Regulatory penalties and reputation damage",
                "probability": 0.7,
                "mitigation": "Accelerate renewable energy transition",
                "status": "Active"
            },
            {
                "id": "R002",
                "name": "Water Scarcity Impact",
                "category": "Environmental",
                "level": "Medium",
                "impact": "Production disruption and community relations",
                "probability": 0.5,
                "mitigation": "Implement water recycling systems",
                "status": "Monitoring"
            },
            {
                "id": "R003",
                "name": "Supply Chain Ethics",
                "category": "Social",
                "level": "Medium",
                "impact": "Brand damage and legal consequences",
                "probability": 0.4,
                "mitigation": "Enhanced supplier auditing",
                "status": "Active"
            },
            {
                "id": "R004",
                "name": "Governance Compliance",
                "category": "Governance",
                "level": "Low",
                "impact": "Legal penalties and investor confidence",
                "probability": 0.2,
                "mitigation": "Governance framework update",
                "status": "Resolved"
            },
            {
                "id": "R005",
                "name": "Climate Adaptation",
                "category": "Environmental",
                "level": "High",
                "impact": "Physical asset damage and business continuity",
                "probability": 0.8,
                "mitigation": "Climate resilience planning",
                "status": "Active"
            }
        ]
        
        return render_template(
            'risk_tracker.html',
            risks=risks,
            nav_sections=nav_context["nav_sections"],
            user_menu=nav_context["user_menu"],
            active_nav="risk-tracker"
        )
    
    @app.route('/analytics')
    def analytics_dashboard():
        """Analytics Dashboard - Advanced visualization of sustainability metrics"""
        # Get navigation context
        nav_context = get_context_for_template()
        
        # Get a mock service instance for data
        try:
            from services.simple_mock_service import MockDataService
            data_service = MockDataService()
            metrics = data_service.get_sustainability_metrics()
            logger.info(f"Retrieved {len(metrics)} metrics from mock service")
        except Exception as e:
            logger.error(f"Failed to get metrics from mock service: {e}")
            metrics = []
        
        # Generate timeframe data for selected metrics
        timeframe_data = {}
        categories = ["Carbon Emissions", "Energy Usage", "Water Usage", "Waste Management"]
        for category in categories:
            # Generate 12 months of data
            month_data = []
            baseline = random.uniform(100, 500)
            for i in range(12):
                # Create some random variation with a slight downward trend
                value = baseline * (1 - (i/24)) + random.uniform(-20, 20)
                month_data.append({
                    "month": (datetime.now() - timedelta(days=30*(11-i))).strftime("%b %Y"),
                    "value": round(max(0, value), 2)
                })
            timeframe_data[category] = month_data
        
        return render_template(
            'analytics.html',
            metrics=metrics,
            timeframe_data=timeframe_data,
            categories=categories,
            nav_sections=nav_context["nav_sections"],
            user_menu=nav_context["user_menu"],
            active_nav="analytics"
        )
    
    @app.route('/story-cards')
    def story_cards():
        """AI Storytelling Engine - Data-driven sustainability narratives with Gartner-inspired methodology"""
        # Get navigation context
        nav_context = get_context_for_template()
        
        # Get parameters
        audience = request.args.get('audience', 'board')
        category = request.args.get('category', 'all')
        
        # Try to get MongoDB stories
        try:
            from mongo_stories import get_stories
            stories = get_stories(category=None if category == 'all' else category, limit=6)
            logger.info(f"Retrieved {len(stories)} stories from MongoDB for audience={audience}, category={category}")
        except Exception as e:
            logger.warning(f"Failed to get stories from MongoDB: {e}")
            stories = []
        
        # Generate mock stories if needed
        if not stories:
            # Audience-specific story templates
            audience_templates = {
                'board': [
                    {
                        "title": "Carbon Reduction Strategy Delivering Results",
                        "content": "Our carbon reduction initiatives have exceeded quarterly targets by 15%. This positions us ahead of regulatory requirements and industry benchmarks.",
                        "category": "Carbon Management",
                        "recommendation": "Increase investment in most effective carbon reduction projects by 10%."
                    },
                    {
                        "title": "Renewable Energy Transition Accelerating",
                        "content": "Renewable energy now accounts for 45% of our total energy mix, up from 30% last year. This exceeds our 2025 roadmap target ahead of schedule.",
                        "category": "Energy",
                        "recommendation": "Accelerate Phase 3 of the renewable energy transition plan."
                    }
                ],
                'investor': [
                    {
                        "title": "ESG Compliance Strengthens Market Position",
                        "content": "Full ESRS compliance achieved, positioning us in the top quartile of our industry. This has resulted in inclusion in two additional ESG-focused indices.",
                        "category": "Governance",
                        "recommendation": "Highlight ESG leadership position in upcoming investor communications."
                    },
                    {
                        "title": "Sustainable Sourcing Reduces Supply Chain Risk",
                        "content": "80% of tier-1 suppliers now meet our enhanced sustainability standards, reducing regulatory and reputational risk exposure by an estimated 35%.",
                        "category": "Supply Chain",
                        "recommendation": "Extend sustainability standards to tier-2 suppliers in high-impact categories."
                    }
                ],
                'sustainability': [
                    {
                        "title": "Water Conservation Projects Exceed Targets",
                        "content": "Water recycling initiatives have reduced freshwater consumption by 28% compared to baseline. Three facilities have achieved water-neutral status.",
                        "category": "Water Management",
                        "recommendation": "Scale successful water recycling technologies to remaining facilities."
                    },
                    {
                        "title": "Waste Diversion Rate at Record High",
                        "content": "Waste diversion rate reached 87% this quarter, with zero waste to landfill achieved at 5 sites. New composting program contributed significantly.",
                        "category": "Waste Management",
                        "recommendation": "Implement advanced waste tracking system to identify remaining improvement opportunities."
                    }
                ]
            }
            
            # Use the appropriate templates based on audience
            templates = audience_templates.get(audience, audience_templates['board'])
            
            # Generate stories based on templates
            stories = []
            for template in templates:
                # Add some randomization
                chart_types = ["line", "bar", "pie", "area"]
                metrics = ["Carbon Emissions", "Energy Usage", "Water Usage", "Waste Reduction", 
                          "Renewable Adoption", "Supplier Compliance", "Community Impact"]
                
                stories.append({
                    "title": template["title"],
                    "content": template["content"],
                    "category": template["category"],
                    "chart_type": random.choice(chart_types),
                    "metrics": random.sample(metrics, 2),
                    "recommendation": template["recommendation"],
                    "audience": audience,
                    "created_at": datetime.now() - timedelta(days=random.randint(1, 14))
                })
            
            # Add some more generic stories
            for i in range(4):
                stories.append({
                    "title": f"Sustainability Insight {i+1}",
                    "content": f"Key finding related to sustainability performance area {i+1}. This represents an important trend for our organization.",
                    "category": random.choice(["Climate Action", "Resource Efficiency", "Social Impact", "Governance"]),
                    "chart_type": random.choice(chart_types),
                    "metrics": random.sample(metrics, 2),
                    "recommendation": f"Strategic recommendation {i+1} based on data analysis.",
                    "audience": audience,
                    "created_at": datetime.now() - timedelta(days=random.randint(1, 14))
                })
                
            logger.info(f"Generated {len(stories)} mock stories for audience={audience}")
        
        # Get available categories for filtering
        categories = list(set(story["category"] for story in stories))
        categories.insert(0, "all")
        
        return render_template(
            'story_cards.html',
            stories=stories,
            audience=audience,
            category=category,
            categories=categories,
            audiences=["board", "investor", "sustainability"],
            nav_sections=nav_context["nav_sections"],
            user_menu=nav_context["user_menu"],
            active_nav="story-cards"
        )
    
    @app.route('/pdf-analyzer')
    def pdf_analyzer():
        """PDF Analyzer - Intelligent document processing for sustainability reports"""
        # Get navigation context
        nav_context = get_context_for_template()
        
        # Get uploaded documents if any
        upload_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
        documents = []
        if os.path.exists(upload_dir):
            for filename in os.listdir(upload_dir):
                if filename.endswith('.pdf'):
                    file_path = os.path.join(upload_dir, filename)
                    file_size = os.path.getsize(file_path)
                    documents.append({
                        "filename": filename,
                        "file_path": file_path,
                        "file_size": file_size,
                        "upload_date": datetime.fromtimestamp(os.path.getctime(file_path))
                    })
        
        return render_template(
            'pdf_analyzer.html',
            documents=documents,
            nav_sections=nav_context["nav_sections"],
            user_menu=nav_context["user_menu"],
            active_nav="pdf-analyzer"
        )
    
    @app.route('/document-upload', methods=['GET', 'POST'])
    def document_upload_route():
        """Document upload with Ethical AI Assessment"""
        # Get navigation context
        nav_context = get_context_for_template()
        
        if request.method == 'POST':
            # Check if the post request has the file part
            if 'document' not in request.files:
                flash('No file part')
                return redirect(request.url)
            
            file = request.files['document']
            
            # If user does not select file, browser also
            # submits an empty part without filename
            if file.filename == '':
                flash('No selected file')
                return redirect(request.url)
            
            if file and file.filename.endswith('.pdf'):
                filename = secure_filename(file.filename)
                upload_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
                os.makedirs(upload_dir, exist_ok=True)
                file_path = os.path.join(upload_dir, filename)
                file.save(file_path)
                
                # Process the document
                try:
                    from document_processor import DocumentProcessor
                    processor = DocumentProcessor()
                    result = processor.process_document(file_path)
                    
                    # Store processing result in session
                    session['document_analysis'] = {
                        'filename': filename,
                        'path': file_path,
                        'analysis': result,
                        'timestamp': datetime.now().isoformat()
                    }
                    
                    flash(f'Document {filename} uploaded and processed successfully')
                    
                    # Redirect to the document analysis page
                    return redirect(url_for('document_analysis', filename=filename))
                except Exception as e:
                    logger.error(f"Error processing document: {e}")
                    flash(f'Error processing document: {str(e)}')
                    return redirect(request.url)
        
        return render_template(
            'document_upload.html',
            nav_sections=nav_context["nav_sections"],
            user_menu=nav_context["user_menu"],
            active_nav="document-upload"
        )
    
    @app.route('/document-analysis/<filename>')
    def document_analysis(filename):
        """Document analysis page with AI-powered querying"""
        # Get navigation context
        nav_context = get_context_for_template()
        
        # Get document analysis from session
        document_analysis = session.get('document_analysis')
        
        if not document_analysis or document_analysis.get('filename') != filename:
            flash('Document analysis not found or expired')
            return redirect(url_for('document_upload_route'))
        
        analysis = document_analysis.get('analysis', {})
        
        # Extract and add the document text to session for API access
        if 'text' not in document_analysis and 'path' in document_analysis:
            try:
                from document_processor import DocumentProcessor
                processor = DocumentProcessor()
                text, page_count = processor.extract_text(document_analysis['path'])
                document_analysis['text'] = text
                document_analysis['page_count'] = page_count
                session['document_analysis'] = document_analysis
                logger.info(f"Added extracted text for {filename} to session")
            except Exception as e:
                logger.error(f"Error extracting text from document: {e}")
        
        # Prepare preview text (first 1000 chars)
        preview_text = document_analysis.get('text', '')[:1000] + '...' if document_analysis.get('text') else ''
        
        # Enrich analysis with document structure if available
        if 'document_structure' not in analysis and document_analysis.get('text'):
            try:
                from document_processor import DocumentProcessor
                processor = DocumentProcessor()
                page_count = document_analysis.get('page_count', 0)
                structure = processor._create_document_structure(document_analysis['text'], page_count)
                analysis['document_structure'] = structure
                logger.info(f"Added document structure for {filename}")
            except Exception as e:
                logger.error(f"Error creating document structure: {e}")
                analysis['document_structure'] = None
        
        # Add preview to analysis
        analysis['preview'] = preview_text
        analysis['page_count'] = document_analysis.get('page_count', 0)
        analysis['word_count'] = len(document_analysis.get('text', '').split()) if document_analysis.get('text') else 0
        
        return render_template(
            'document_analysis.html',
            filename=filename,
            analysis=analysis,
            nav_sections=nav_context["nav_sections"],
            user_menu=nav_context["user_menu"],
            active_nav="document-upload"
        )
    
    @app.route('/data-terminal')
    def data_terminal():
        """Data Terminal - Minimal API interface for programmatic data access"""
        # Get navigation context
        nav_context = get_context_for_template()
        
        # Get available endpoints
        endpoints = [
            {
                "name": "Metrics API",
                "path": "/api/metrics",
                "description": "Access sustainability metrics data",
                "methods": ["GET"],
                "parameters": [
                    {"name": "category", "type": "string", "required": False, "description": "Filter by category"},
                    {"name": "start_date", "type": "date", "required": False, "description": "Start date for time range"},
                    {"name": "end_date", "type": "date", "required": False, "description": "End date for time range"}
                ]
            },
            {
                "name": "Trends API",
                "path": "/api/trends",
                "description": "Access sustainability trend data",
                "methods": ["GET"],
                "parameters": [
                    {"name": "category", "type": "string", "required": False, "description": "Filter by category"},
                    {"name": "min_virality", "type": "number", "required": False, "description": "Minimum virality score"}
                ]
            },
            {
                "name": "Storytelling API",
                "path": "/api/storytelling",
                "description": "Generate data-driven sustainability narratives",
                "methods": ["POST"],
                "parameters": [
                    {"name": "metric", "type": "string", "required": True, "description": "Target metric"},
                    {"name": "audience", "type": "string", "required": True, "description": "Target audience"},
                    {"name": "narrative_focus", "type": "string", "required": False, "description": "Narrative focus"}
                ]
            },
            {
                "name": "Search API",
                "path": "/api/search",
                "description": "Search sustainability content",
                "methods": ["GET"],
                "parameters": [
                    {"name": "query", "type": "string", "required": True, "description": "Search query"},
                    {"name": "mode", "type": "string", "required": False, "description": "Search mode (hybrid, keyword, vector)"}
                ]
            }
        ]
        
        return render_template(
            'data_terminal.html',
            endpoints=endpoints,
            nav_sections=nav_context["nav_sections"],
            user_menu=nav_context["user_menu"],
            active_nav="data-terminal"
        )
    
    @app.route('/sustainability-strategies')
    def sustainability_strategies():
        """Sustainability Strategies - Strategic frameworks and implementation plans"""
        # Get navigation context
        nav_context = get_context_for_template()
        
        # Generate mock strategies
        strategies = [
            {
                "name": "Carbon Neutrality Roadmap",
                "description": "Comprehensive strategy to achieve carbon neutrality by 2030",
                "timeframe": "2023-2030",
                "key_initiatives": [
                    "Renewable energy transition",
                    "Fleet electrification",
                    "Process efficiency improvements",
                    "Carbon offsetting program"
                ],
                "status": "Active",
                "completion": 25
            },
            {
                "name": "Water Stewardship Plan",
                "description": "Framework for responsible water management and conservation",
                "timeframe": "2022-2028",
                "key_initiatives": [
                    "Water recycling systems",
                    "Rainwater harvesting",
                    "Process water reduction",
                    "Watershed protection"
                ],
                "status": "Active",
                "completion": 40
            },
            {
                "name": "Circular Economy Transition",
                "description": "Strategic approach to eliminate waste and maximize resource value",
                "timeframe": "2023-2029",
                "key_initiatives": [
                    "Product lifecycle redesign",
                    "Take-back programs",
                    "Recycled content integration",
                    "Zero waste to landfill"
                ],
                "status": "Planning",
                "completion": 10
            },
            {
                "name": "Sustainable Supply Chain",
                "description": "Framework for embedding sustainability throughout the supply chain",
                "timeframe": "2022-2027",
                "key_initiatives": [
                    "Supplier sustainability assessment",
                    "Code of conduct implementation",
                    "Logistics optimization",
                    "Scope 3 emissions reduction"
                ],
                "status": "Active",
                "completion": 35
            }
        ]
        
        return render_template(
            'sustainability_strategies.html',
            strategies=strategies,
            nav_sections=nav_context["nav_sections"],
            user_menu=nav_context["user_menu"],
            active_nav="sustainability-strategies"
        )
    
    @app.route('/monetization-opportunities')
    def monetization_opportunities():
        """Monetization Opportunities - Strategic insights for sustainable business models"""
        # Get navigation context
        nav_context = get_context_for_template()
        
        # Get monetization data
        try:
            from monetization_strategies import get_monetization_strategies
            monetization_data = get_monetization_strategies()
        except Exception as e:
            logger.error(f"Error getting monetization strategies: {e}")
            # Fallback monetization data
            monetization_data = {
                "M1": {
                    "name": "Sustainability Premium Product Lines",
                    "description": "Develop premium product lines with enhanced sustainability credentials"
                },
                "M2": {
                    "name": "Sustainability Data Monetization",
                    "description": "Monetize sustainability data insights through subscription services"
                },
                "M3": {
                    "name": "Circular Business Models",
                    "description": "Implement circular business models to create new revenue streams"
                },
                "M4": {
                    "name": "Sustainability Consulting Services",
                    "description": "Offer sustainability consulting services based on internal expertise"
                },
                "M5": {
                    "name": "Green Financing Opportunities",
                    "description": "Leverage green financing mechanisms to fund sustainability initiatives"
                }
            }
        
        # Generate opportunity assessments
        opportunities = []
        for key, data in monetization_data.items():
            opportunities.append({
                "id": key,
                "name": data["name"],
                "description": data["description"],
                "potential": random.choice(["High", "Medium", "Low"]),
                "timeframe": random.choice(["Short-term", "Medium-term", "Long-term"]),
                "complexity": random.choice(["Low", "Medium", "High"]),
                "investment": "$" + str(random.randint(1, 10)) + ("M" if random.random() > 0.5 else "00K"),
                "roi_potential": str(random.randint(15, 50)) + "%"
            })
        
        return render_template(
            'monetization_opportunities.html',
            opportunities=opportunities,
            nav_sections=nav_context["nav_sections"],
            user_menu=nav_context["user_menu"],
            active_nav="monetization-opportunities"
        )
    
    @app.route('/co-pilot')
    def co_pilot():
        """Sustainability Co-Pilot - Contextual AI assistant for sustainability intelligence"""
        # Get navigation context
        nav_context = get_context_for_template()
        
        # Get query if any
        query = request.args.get('query', '')
        
        # Process query if provided
        response = {}
        if query:
            try:
                # Get response from API if available
                try:
                    from sustainability_copilot import get_copilot_response
                    response = get_copilot_response(query)
                except Exception as e:
                    logger.error(f"Error getting copilot response: {e}")
                    # Generate mock response
                    response = {
                        "answer": f"Here's what I found about '{query}'...",
                        "sources": [
                            {"title": "Source 1", "url": "#", "snippet": "Relevant information from source 1"},
                            {"title": "Source 2", "url": "#", "snippet": "Relevant information from source 2"}
                        ],
                        "related_queries": [
                            f"{query} trends",
                            f"{query} strategies",
                            f"{query} metrics"
                        ]
                    }
            except Exception as e:
                logger.error(f"Error processing query: {e}")
                response = {
                    "error": str(e)
                }
        
        return render_template(
            'co_pilot.html',
            query=query,
            response=response,
            nav_sections=nav_context["nav_sections"],
            user_menu=nav_context["user_menu"],
            active_nav="co-pilot"
        )
    
    # API endpoints
    @app.route('/api/metrics')
    def api_metrics():
        """API endpoint for metrics data"""
        logger.info("API metrics endpoint accessed")
        
        # Get query parameters
        category = request.args.get('category')
        
        try:
            # Try to get metrics from MongoDB
            try:
                from mongo_metrics import get_metrics
                metrics = get_metrics(
                    category=category,
                    limit=int(request.args.get('limit', 100))
                )
                logger.info(f"Retrieved {len(metrics)} metrics from MongoDB")
            except Exception as e:
                logger.warning(f"Failed to get metrics from MongoDB: {e}")
                metrics = []
            
            # Get from mock service if needed
            if not metrics:
                try:
                    from services.simple_mock_service import MockDataService
                    mock_service = MockDataService()
                    metrics = mock_service.get_sustainability_metrics()
                    
                    # Apply category filter if specified
                    if category:
                        metrics = [m for m in metrics if m.get('category') == category]
                    
                    logger.info(f"Retrieved {len(metrics)} metrics from mock service")
                except Exception as e:
                    logger.error(f"Error getting metrics from mock service: {e}")
                    metrics = []
            
            # Format for JSON serialization
            for metric in metrics:
                if isinstance(metric.get('date'), datetime):
                    metric['date'] = metric['date'].isoformat()
                if isinstance(metric.get('created_at'), datetime):
                    metric['created_at'] = metric['created_at'].isoformat()
            
            return jsonify({
                "status": "success",
                "metrics": metrics,
                "count": len(metrics)
            })
        except Exception as e:
            logger.error(f"Error in API metrics endpoint: {e}")
            return jsonify({
                "status": "error",
                "message": str(e)
            }), 500
    
    @app.route('/api/trends')
    def api_trends():
        """API endpoint for trend data"""
        logger.info("API trends endpoint accessed")
        
        # Get query parameters
        category = request.args.get('category')
        min_virality = request.args.get('min_virality')
        
        try:
            # Try to get trends from MongoDB
            try:
                from mongo_trends import get_trends
                trends = get_trends(
                    category=category,
                    min_virality=float(min_virality) if min_virality else None,
                    limit=int(request.args.get('limit', 100))
                )
                logger.info(f"Retrieved {len(trends)} trends from MongoDB")
            except Exception as e:
                logger.warning(f"Failed to get trends from MongoDB: {e}")
                trends = []
            
            # Generate mock trends if needed
            if not trends:
                # Categories
                categories = ["Climate Action", "Resource Efficiency", "Social Impact", "Governance", "Supply Chain"]
                if category:
                    categories = [c for c in categories if c == category]
                
                # Generate mock trends
                trends = []
                for i in range(20):
                    trend_category = random.choice(categories)
                    virality_score = random.uniform(50, 100)
                    
                    # Skip if below minimum virality
                    if min_virality and virality_score < float(min_virality):
                        continue
                    
                    trends.append({
                        "id": str(i),
                        "name": f"{trend_category} Trend {i+1}",
                        "category": trend_category,
                        "virality_score": virality_score,
                        "momentum": random.choice(["increasing", "decreasing", "stable"]),
                        "created_at": datetime.now() - timedelta(days=i % 30)
                    })
                logger.info(f"Generated {len(trends)} mock trends")
            
            # Format for JSON serialization
            for trend in trends:
                if isinstance(trend.get('created_at'), datetime):
                    trend['created_at'] = trend['created_at'].isoformat()
            
            return jsonify({
                "status": "success",
                "trends": trends,
                "count": len(trends)
            })
        except Exception as e:
            logger.error(f"Error in API trends endpoint: {e}")
            return jsonify({
                "status": "error",
                "message": str(e)
            }), 500
    
    @app.route('/api/storytelling', methods=['POST'])
    def api_storytelling():
        """
        API endpoint for AI storytelling generation with Gartner-inspired methodology
        
        Request body:
        {
            "metric": "Carbon Emissions",
            "time_period": "Q2 2023",
            "narrative_focus": "trends",
            "audience": "board",
            "context": "regulatory compliance",
            "chart_type": "line"
        }
        
        Response:
        {
            "status": "success",
            "story": {
                "title": "Carbon Emissions Reduction Exceeding Targets",
                "content": "...",
                "chart_data": {...},
                "chart_type": "line",
                "key_insight": "...",
                "recommendation": "..."
            }
        }
        """
        logger.info("API storytelling endpoint accessed")
        
        try:
            # Get request data
            data = request.json
            
            if not data:
                return jsonify({
                    "status": "error",
                    "message": "No data provided"
                }), 400
            
            # Get parameters
            metric = data.get('metric', 'Carbon Emissions')
            time_period = data.get('time_period', 'Q2 2023')
            narrative_focus = data.get('narrative_focus', 'trends')
            audience = data.get('audience', 'board')
            context = data.get('context', 'regulatory compliance')
            chart_type = data.get('chart_type', 'line')
            
            # Get data sources
            try:
                # Try to get data from MongoDB
                has_mongo_data = False
                
                try:
                    from mongo_metrics import get_metrics
                    from mongo_trends import get_trends
                    from mongo_stories import get_stories
                    
                    metrics = get_metrics(limit=20)
                    trends = get_trends(limit=10)
                    stories = get_stories(limit=5)
                    
                    has_mongo_data = len(metrics) > 0 or len(trends) > 0 or len(stories) > 0
                    
                    source_data = {
                        "metrics": metrics,
                        "trends": trends,
                        "stories": stories
                    }
                except Exception as e:
                    logger.warning(f"Failed to get data from MongoDB: {e}")
                    has_mongo_data = False
                
                if not has_mongo_data:
                    # Fallback to mock service
                    try:
                        from services.simple_mock_service import MockDataService
                        mock_service = MockDataService()
                        
                        metrics = mock_service.get_sustainability_metrics()
                        trends = mock_service.get_sustainability_trends()
                        stories = mock_service.get_sustainability_stories()
                        
                        source_data = {
                            "metrics": metrics,
                            "trends": trends,
                            "stories": stories
                        }
                    except Exception as e:
                        logger.error(f"Error getting data from mock service: {e}")
                        # Provide minimal mock data
                        source_data = {
                            "metrics": [],
                            "trends": [],
                            "stories": []
                        }
            except Exception as e:
                logger.error(f"Error preparing data sources: {e}")
                source_data = {
                    "metrics": [],
                    "trends": [],
                    "stories": []
                }
            
            # Create story card
            story = create_story_card(
                metric=metric,
                time_period=time_period,
                narrative_focus=narrative_focus,
                audience=audience,
                context=context,
                chart_type=chart_type,
                source_data=source_data
            )
            
            return jsonify({
                "status": "success",
                "story": story
            })
        except Exception as e:
            logger.error(f"Error in API storytelling endpoint: {e}")
            return jsonify({
                "status": "error",
                "message": str(e)
            }), 500

def create_story_card(
    metric: str,
    time_period: str,
    narrative_focus: str,
    audience: str,
    context: str,
    chart_type: str,
    source_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Create a story card with AI-driven narrative and visualization
    
    Args:
        metric: Target metric for the story
        time_period: Timeframe for analysis
        narrative_focus: Focus of the narrative
        audience: Target stakeholder audience
        context: Additional context
        chart_type: Chart type preference
        source_data: Data sources for storytelling
        
    Returns:
        Dictionary containing the story card data
    """
    logger.info(f"Creating {audience}-focused story card for {metric}")
    
    # Check if we have any data to work with
    metrics = source_data.get('metrics', [])
    trends = source_data.get('trends', [])
    
    # Get stories from MongoDB or fallback source
    try:
        from mongo_stories import get_stories
        stories = get_stories(limit=5)
    except Exception:
        stories = source_data.get('stories', [])
    
    # Find relevant metrics for the story
    relevant_metrics = [m for m in metrics if metric.lower() in m.get('name', '').lower()]
    
    # Generate story content
    if relevant_metrics:
        # Use actual metrics data
        target_metric = relevant_metrics[0]
        metric_name = target_metric.get('name', metric)
        metric_value = target_metric.get('value', random.uniform(50, 500))
        metric_unit = target_metric.get('unit', 'tons')
        metric_trend = target_metric.get('trend', random.choice(['increasing', 'decreasing', 'stable']))
    else:
        # Generate mock data
        metric_name = metric
        metric_value = random.uniform(50, 500)
        metric_unit = 'tons' if 'carbon' in metric.lower() else 'units'
        metric_trend = random.choice(['increasing', 'decreasing', 'stable'])
    
    # Narrative generation based on audience
    if audience == 'board':
        # Board-focused narrative (strategic, risk-oriented)
        if metric_trend == 'decreasing':
            title = f"{metric_name} Reduction Exceeding Targets"
            content = f"Our {metric_name.lower()} has decreased to {metric_value:.1f} {metric_unit}, outperforming our quarterly target by 15%. This positions us ahead of regulatory requirements and industry benchmarks for {time_period}."
            key_insight = "Performance is significantly better than industry average, providing competitive advantage."
            recommendation = f"Maintain current {metric_name.lower()} reduction strategies while exploring potential for accelerated targets."
        elif metric_trend == 'increasing':
            title = f"{metric_name} Increase Requires Attention"
            content = f"Our {metric_name.lower()} has increased to {metric_value:.1f} {metric_unit}, exceeding our quarterly threshold by 12%. This creates potential regulatory and reputation exposure that requires board attention for {time_period}."
            key_insight = f"The {metric_trend} trend presents medium-term strategic risk if not addressed."
            recommendation = f"Implement the prepared contingency plan for {metric_name.lower()} management and adjust quarterly targets."
        else:
            title = f"{metric_name} Performance Stable"
            content = f"Our {metric_name.lower()} remained stable at {metric_value:.1f} {metric_unit}, consistent with expectations for {time_period}. Current performance remains in compliance with regulatory requirements and aligned with industry benchmarks."
            key_insight = "Stability indicates effective controls but may hide potential areas for improvement."
            recommendation = f"Review {metric_name.lower()} management program for further optimization opportunities."
    elif audience == 'investor':
        # Investor-focused narrative (financial, competitive)
        if metric_trend == 'decreasing':
            title = f"{metric_name} Improvement Strengthens Market Position"
            content = f"Our {metric_name.lower()} reduction to {metric_value:.1f} {metric_unit} represents a performance improvement that has resulted in a 2-point gain in our ESG rating for {time_period}. This outperformance supports inclusion in additional sustainability indices."
            key_insight = "This improvement has positive implications for cost of capital and index inclusion criteria."
            recommendation = f"Highlight {metric_name.lower()} leadership position in upcoming investor communications."
        elif metric_trend == 'increasing':
            title = f"{metric_name} Rise Creates Potential Risk Exposure"
            content = f"Our {metric_name.lower()} has increased to {metric_value:.1f} {metric_unit}, creating potential ESG rating pressure. This increase may impact our sustainability index position for {time_period} if not effectively managed."
            key_insight = f"The {metric_trend} trend may affect sustainability ratings but mitigation plans are in place."
            recommendation = "Develop proactive investor communication strategy about mitigation plans and timeline."
        else:
            title = f"{metric_name} Stability Maintains ESG Position"
            content = f"Our {metric_name.lower()} remained stable at {metric_value:.1f} {metric_unit} for {time_period}, preserving our current ESG score in this category. This stability supports our current position in sustainability indices."
            key_insight = "Our performance remains competitive within our industry peer group."
            recommendation = "Continue current performance while benchmarking against best-in-class peer performance."
    else:
        # Sustainability team narrative (operational, detailed)
        if metric_trend == 'decreasing':
            title = f"{metric_name} Reduction Shows Program Success"
            content = f"Our {metric_name.lower()} decreased to {metric_value:.1f} {metric_unit} during {time_period}, representing successful implementation of our sustainability initiatives. Key contributing factors include process optimization and technology upgrades."
            key_insight = "Three facilities contributed 65% of the total reduction, indicating potential for similar results at other locations."
            recommendation = "Scale successful reduction techniques to remaining facilities with similar profiles."
        elif metric_trend == 'increasing':
            title = f"{metric_name} Increase Requires Intervention"
            content = f"Our {metric_name.lower()} increased to {metric_value:.1f} {metric_unit} during {time_period}, primarily due to production volume increase and one-time equipment issues. Immediate intervention is needed to return to target trajectory."
            key_insight = "Root cause analysis identified two key factors that can be addressed within this quarter."
            recommendation = "Implement the identified short-term corrective actions while evaluating medium-term efficiency projects."
        else:
            title = f"{metric_name} Performance Steady Despite Growth"
            content = f"Our {metric_name.lower()} remained stable at {metric_value:.1f} {metric_unit} for {time_period}, even as production increased by 8%. This indicates improving efficiency but may hide opportunities for absolute reduction."
            key_insight = "Efficiency improvements are offsetting growth impacts, but absolute reduction remains the goal."
            recommendation = "Continue efficiency improvements while evaluating absolute reduction opportunities."
    
    # Generate chart data
    if chart_type == 'line':
        chart_data = generate_line_chart_data(metric_name, metric_value, metric_trend)
    elif chart_type == 'bar':
        chart_data = generate_bar_chart_data(metric_name, metric_value, metric_trend)
    elif chart_type == 'pie':
        chart_data = generate_pie_chart_data(metric_name, metric_value)
    else:
        chart_data = generate_line_chart_data(metric_name, metric_value, metric_trend)
    
    # Assemble the story card
    story = {
        "title": title,
        "content": content,
        "metric": metric_name,
        "value": metric_value,
        "unit": metric_unit,
        "trend": metric_trend,
        "time_period": time_period,
        "chart_data": chart_data,
        "chart_type": chart_type,
        "key_insight": key_insight,
        "recommendation": recommendation,
        "audience": audience,
        "context": context,
        "created_at": datetime.now().isoformat()
    }
    
    return story

def generate_line_chart_data(metric_name, current_value, trend):
    """Generate line chart data for storytelling"""
    # Generate 6 months of data
    months = []
    values = []
    
    for i in range(6):
        # Create month label (most recent last)
        month = (datetime.now() - timedelta(days=30*(5-i))).strftime("%b")
        months.append(month)
        
        # Create values with appropriate trend
        if trend == 'decreasing':
            # Decreasing trend with slight variations
            value = current_value * (1 + (i-5)/10) + random.uniform(-current_value*0.05, current_value*0.05)
        elif trend == 'increasing':
            # Increasing trend with slight variations
            value = current_value * (1 - (i-5)/10) + random.uniform(-current_value*0.05, current_value*0.05)
        else:
            # Stable trend with variations
            value = current_value + random.uniform(-current_value*0.08, current_value*0.08)
        
        values.append(max(0, value))
    
    return {
        "labels": months,
        "datasets": [
            {
                "label": metric_name,
                "data": values,
                "fill": False,
                "borderColor": "#48a999",
                "tension": 0.1
            }
        ]
    }

def generate_bar_chart_data(metric_name, current_value, trend):
    """Generate bar chart data for storytelling"""
    # Generate comparison data for different locations or categories
    locations = ["Site A", "Site B", "Site C", "Site D", "Site E"]
    values = []
    
    # Create values with a distribution that makes sense
    total = 0
    for i in range(len(locations)):
        # Create a reasonable distribution
        if i == 0:  # Make first location the highest or lowest based on trend
            if trend == 'decreasing':
                value = current_value * 0.4 * random.uniform(0.8, 1.2)
            else:
                value = current_value * 0.6 * random.uniform(0.8, 1.2)
        else:
            value = current_value * random.uniform(0.1, 0.3)
        
        values.append(max(0, value))
        total += value
    
    # Adjust to make sum approximately equal to current_value
    scale_factor = current_value / total
    values = [v * scale_factor for v in values]
    
    return {
        "labels": locations,
        "datasets": [
            {
                "label": metric_name,
                "data": values,
                "backgroundColor": [
                    "#48a999", "#3d8880", "#32676a", "#264854", "#1a293d"
                ]
            }
        ]
    }

def generate_pie_chart_data(metric_name, current_value):
    """Generate pie chart data for storytelling"""
    # Generate breakdown data for different categories or components
    categories = ["Category A", "Category B", "Category C", "Category D"]
    values = []
    
    # Create values with a distribution that makes sense
    total = 0
    for i in range(len(categories)):
        # Create a reasonable distribution
        value = current_value * random.uniform(0.1, 0.4)
        values.append(max(0, value))
        total += value
    
    # Adjust to make sum approximately equal to current_value
    scale_factor = current_value / total
    values = [v * scale_factor for v in values]
    
    return {
        "labels": categories,
        "datasets": [
            {
                "data": values,
                "backgroundColor": [
                    "#48a999", "#3d8880", "#32676a", "#264854"
                ]
            }
        ]
    }

    @app.route('/api/search')
    def api_search():
        """Unified search API endpoint"""
        logger.info("API search endpoint accessed")
        
        # Get query parameters
        query = request.args.get('query', '')
        mode = request.args.get('mode', 'hybrid')
        
        if not query:
            return jsonify({
                "status": "error",
                "message": "No query provided"
            }), 400
        
        try:
            # Try to use enhanced search if available
            try:
                from enhanced_search import perform_search
                
                # Convert to async result
                import asyncio
                result = asyncio.run(perform_search(
                    query=query,
                    mode=mode,
                    max_results=int(request.args.get('limit', 20))
                ))
                
                return jsonify({
                    "status": "success",
                    "results": result
                })
            except ImportError:
                logger.warning("Enhanced search not available, using fallback")
                # Continue to fallback
            
            # Fallback to simple mock search
            results = []
            categories = ["Climate Action", "Resource Efficiency", "Social Impact", "Governance"]
            
            for i in range(10):
                category = categories[i % len(categories)]
                results.append({
                    "title": f"Search result {i+1} for '{query}'",
                    "url": f"https://example.com/result/{i}",
                    "snippet": f"This is a snippet for search result {i+1} related to {category} and matching '{query}'...",
                    "source": f"Source {i+1}",
                    "date": (datetime.now() - timedelta(days=i)).isoformat(),
                    "category": category,
                    "relevance": max(0.3, 0.95 - (i * 0.07))
                })
            
            return jsonify({
                "status": "success",
                "query": query,
                "mode": mode,
                "results": results,
                "meta": {
                    "total_results": len(results),
                    "processing_time_ms": random.randint(100, 500)
                }
            })
        except Exception as e:
            logger.error(f"Error in API search endpoint: {e}")
            return jsonify({
                "status": "error",
                "message": str(e)
            }), 500
    
    @app.route('/api/search')
    def api_search():
        """Unified search API endpoint"""
        logger.info("API search endpoint accessed")
        
        # Get query parameters
        query = request.args.get('query', '')
        mode = request.args.get('mode', 'hybrid')
        
        if not query:
            return jsonify({
                "status": "error",
                "message": "No query provided"
            }), 400
        
        try:
            # Try to use enhanced search if available
            try:
                from enhanced_search import perform_search
                
                # Convert to async result
                import asyncio
                result = asyncio.run(perform_search(
                    query=query,
                    mode=mode,
                    max_results=int(request.args.get('limit', 20))
                ))
                
                return jsonify({
                    "status": "success",
                    "results": result
                })
            except ImportError:
                logger.warning("Enhanced search not available, using fallback")
                # Continue to fallback
            
            # Fallback to simple mock search
            results = []
            categories = ["Climate Action", "Resource Efficiency", "Social Impact", "Governance"]
            
            for i in range(10):
                category = categories[i % len(categories)]
                results.append({
                    "title": f"Search result {i+1} for '{query}'",
                    "url": f"https://example.com/result/{i}",
                    "snippet": f"This is a snippet for search result {i+1} related to {category} and matching '{query}'...",
                    "source": f"Source {i+1}",
                    "date": (datetime.now() - timedelta(days=i)).isoformat(),
                    "category": category,
                    "relevance": max(0.3, 0.95 - (i * 0.07))
                })
            
            return jsonify({
                "status": "success",
                "query": query,
                "mode": mode,
                "results": results,
                "meta": {
                    "total_results": len(results),
                    "processing_time_ms": random.randint(100, 500)
                }
            })
        except Exception as e:
            logger.error(f"Error in API search endpoint: {e}")
            return jsonify({
                "status": "error",
                "message": str(e)
            }), 500
    
    @app.route('/api/copilot', methods=['POST'])
    def api_copilot():
        """API endpoint for Co-Pilot AI assistant"""
        logger.info("API copilot endpoint accessed")
        
        try:
            # Get request data
            data = request.json
            
            if not data:
                return jsonify({
                    "status": "error",
                    "message": "No data provided"
                }), 400
            
            query = data.get('query', '')
            context = data.get('context', {})
            
            if not query:
                return jsonify({
                    "status": "error",
                    "message": "No query provided"
                }), 400
            
            # Try to use sustainability copilot if available
            try:
                from sustainability_copilot import get_copilot_response
                response = get_copilot_response(query, context)
                return jsonify({
                    "status": "success",
                    "response": response
                })
            except ImportError:
                logger.warning("Sustainability copilot not available, using fallback")
                # Continue to fallback
            
            # Generate a fallback response
            response = {
                "answer": f"Here's what I found about '{query}'...\n\nBased on sustainability best practices, this query relates to important ESG factors that organizations should consider in their reporting and strategy.",
                "sources": [
                    {
                        "title": "Sustainability Best Practices",
                        "url": "https://example.com/best-practices",
                        "snippet": "Organizations should consider their environmental impact and establish clear metrics for measurement."
                    },
                    {
                        "title": "ESG Reporting Guidelines",
                        "url": "https://example.com/esg-guidelines",
                        "snippet": "Transparent reporting of sustainability metrics is essential for stakeholder trust."
                    }
                ],
                "related_queries": [
                    f"{query} metrics",
                    f"{query} reporting",
                    f"{query} best practices"
                ]
            }
            
            return jsonify({
                "status": "success",
                "response": response
            })
        except Exception as e:
            logger.error(f"Error in API copilot endpoint: {e}")
            return jsonify({
                "status": "error",
                "message": str(e)
            }), 500
    
    @app.route('/api/summarize', methods=['POST'])
    def api_summarize():
        """API endpoint to summarize sustainability text using AI"""
        logger.info("API summarize endpoint accessed")
        
        try:
            # Get request data
            data = request.json
            
            if not data:
                return jsonify({
                    "status": "error",
                    "message": "No data provided"
                }), 400
            
            text = data.get('text', '')
            max_length = data.get('max_length', 3)
            
            if not text:
                return jsonify({
                    "status": "error",
                    "message": "No text provided"
                }), 400
            
            # Generate a simple summary (production version would use an actual AI model)
            words = text.split()
            if len(words) <= 50:
                summary = text
            else:
                # Extract first few sentences as summary
                sentences = text.split('.')
                summary = '. '.join(sentences[:max_length]) + '.'
            
            return jsonify({
                "status": "success",
                "original_length": len(text),
                "summary_length": len(summary),
                "summary": summary
            })
        except Exception as e:
            logger.error(f"Error in API summarize endpoint: {e}")
            return jsonify({
                "status": "error",
                "message": str(e)
            }), 500
    
    @app.route('/api/predictive-analytics')
    def api_predictive_analytics():
        """API endpoint for predictive analytics of sustainability metrics"""
        logger.info("API predictive analytics endpoint accessed")
        
        try:
            # Get query parameters
            metric = request.args.get('metric', 'Carbon Emissions')
            timeframe = request.args.get('timeframe', '12')
            
            # Generate predictive data
            current_value = random.uniform(100, 500)
            historical_data = []
            predicted_data = []
            
            # Generate 12 months of historical data
            for i in range(12):
                month = (datetime.now() - timedelta(days=30*(11-i))).strftime("%b %Y")
                value = current_value * (1 + (i-11)/24) + random.uniform(-25, 25)
                historical_data.append({
                    "date": month,
                    "value": max(0, value)
                })
            
            # Generate predicted data
            for i in range(int(timeframe)):
                month = (datetime.now() + timedelta(days=30*(i+1))).strftime("%b %Y")
                
                # Add slight downward trend plus some randomness
                value = current_value * (1 - (i+1)/48) + random.uniform(-20, 15)
                
                predicted_data.append({
                    "date": month,
                    "value": max(0, value),
                    "upper_bound": max(0, value * 1.15),
                    "lower_bound": max(0, value * 0.85)
                })
            
            return jsonify({
                "status": "success",
                "metric": metric,
                "current_value": current_value,
                "historical_data": historical_data,
                "predicted_data": predicted_data,
                "insights": [
                    "Based on current trends, we expect a 12% reduction over the next year",
                    "Seasonal variations are evident with higher values in Q3",
                    "Current mitigation strategies are showing positive effects",
                    "Additional measures could accelerate the downward trend"
                ]
            })
        except Exception as e:
            logger.error(f"Error in API predictive analytics endpoint: {e}")
            return jsonify({
                "status": "error",
                "message": str(e)
            }), 500
    
    @app.route('/api/sustainability-analysis', methods=['POST'])
    def api_sustainability_analysis():
        """API endpoint for sustainability analysis"""
        logger.info("API sustainability analysis endpoint accessed")
        
        try:
            # Get request data
            data = request.json
            
            if not data:
                return jsonify({
                    "status": "error",
                    "message": "No data provided"
                }), 400
            
            industry = data.get('industry', 'Manufacturing')
            company_size = data.get('company_size', 'Medium')
            metrics = data.get('metrics', {})
            
            # Generate analysis
            analysis = {
                "overall_score": random.uniform(60, 85),
                "category_scores": {
                    "Environmental": random.uniform(55, 90),
                    "Social": random.uniform(65, 85),
                    "Governance": random.uniform(70, 90)
                },
                "industry_comparison": {
                    "percentile": random.uniform(60, 80),
                    "average_score": random.uniform(55, 75)
                },
                "strengths": [
                    "Strong carbon reduction initiatives",
                    "Comprehensive waste management program",
                    "Clear sustainability governance structure"
                ],
                "improvement_areas": [
                    "Supply chain sustainability monitoring",
                    "Water usage reduction strategies",
                    "Circular economy implementation"
                ],
                "recommendations": [
                    "Implement water recycling systems at key facilities",
                    "Expand supplier sustainability assessment program",
                    "Develop clear carbon neutrality roadmap"
                ]
            }
            
            return jsonify({
                "status": "success",
                "industry": industry,
                "company_size": company_size,
                "analysis": analysis
            })
        except Exception as e:
            logger.error(f"Error in API sustainability analysis endpoint: {e}")
            return jsonify({
                "status": "error",
                "message": str(e)
            }), 500
    
    @app.route('/api/monetization-strategy', methods=['POST'])
    def api_monetization_strategy():
        """API endpoint for monetization strategy recommendations"""
        logger.info("API monetization strategy endpoint accessed")
        
        try:
            # Get request data
            data = request.json
            
            if not data:
                return jsonify({
                    "status": "error",
                    "message": "No data provided"
                }), 400
            
            # Generate recommendations
            recommendations = [
                {
                    "name": "Sustainability Premium Product Lines",
                    "description": "Develop premium product lines with enhanced sustainability credentials",
                    "potential": "High",
                    "implementation_timeline": "6-12 months",
                    "required_investment": "$$$",
                    "roi_potential": "25-40%"
                },
                {
                    "name": "Sustainability Data Monetization",
                    "description": "Monetize sustainability data insights through subscription services",
                    "potential": "Medium",
                    "implementation_timeline": "3-6 months",
                    "required_investment": "$$",
                    "roi_potential": "15-30%"
                },
                {
                    "name": "Circular Economy Business Model",
                    "description": "Implement take-back programs and refurbishment services",
                    "potential": "High",
                    "implementation_timeline": "12-18 months",
                    "required_investment": "$$$",
                    "roi_potential": "20-35%"
                }
            ]
            
            return jsonify({
                "status": "success",
                "recommendations": recommendations
            })
        except Exception as e:
            logger.error(f"Error in API monetization strategy endpoint: {e}")
            return jsonify({
                "status": "error",
                "message": str(e)
            }), 500
    
    @app.route('/api/apa-strategy', methods=['POST'])
    def api_apa_strategy():
        """API endpoint for Assess-Plan-Act (APA) sustainability strategy"""
        logger.info("API APA strategy endpoint accessed")
        
        try:
            # Get request data
            data = request.json
            
            if not data:
                return jsonify({
                    "status": "error",
                    "message": "No data provided"
                }), 400
            
            # Generate APA strategy
            strategy = {
                "assess": {
                    "metrics": [
                        "Carbon Footprint",
                        "Water Usage",
                        "Waste Generation",
                        "Energy Efficiency",
                        "Supplier Sustainability"
                    ],
                    "benchmarks": [
                        "Industry average performance",
                        "Regulatory requirements",
                        "Science-based targets",
                        "Peer company comparison"
                    ],
                    "assessment_tools": [
                        "Carbon accounting software",
                        "Materiality assessment",
                        "Lifecycle assessment",
                        "Supplier assessment questionnaire"
                    ]
                },
                "plan": {
                    "strategic_initiatives": [
                        "Carbon reduction program",
                        "Circular economy transition",
                        "Water conservation strategy",
                        "Sustainable procurement policy"
                    ],
                    "implementation_roadmap": [
                        "Phase 1: Establish baseline (Q1-Q2)",
                        "Phase 2: Pilot initiatives (Q2-Q3)",
                        "Phase 3: Full implementation (Q3-Q4)",
                        "Phase 4: Monitoring and reporting (Ongoing)"
                    ],
                    "resource_requirements": [
                        "Sustainability team expansion",
                        "Data management systems",
                        "Training and capacity building",
                        "Capital investment for efficiency upgrades"
                    ]
                },
                "act": {
                    "implementation_steps": [
                        "Establish governance structure",
                        "Deploy monitoring systems",
                        "Execute pilot projects",
                        "Scale successful initiatives",
                        "Report progress to stakeholders"
                    ],
                    "key_performance_indicators": [
                        "Carbon emissions reduction percentage",
                        "Water usage reduction percentage",
                        "Waste diversion rate",
                        "Renewable energy adoption percentage",
                        "Sustainable supplier percentage"
                    ],
                    "continuous_improvement": [
                        "Quarterly review meetings",
                        "Annual strategy refinement",
                        "Stakeholder feedback integration",
                        "Emerging trend monitoring"
                    ]
                }
            }
            
            return jsonify({
                "status": "success",
                "strategy": strategy
            })
        except Exception as e:
            logger.error(f"Error in API APA strategy endpoint: {e}")
            return jsonify({
                "status": "error",
                "message": str(e)
            }), 500
    
    # Redirect routes
    @app.route('/search')
    def search_redirect():
        """Search redirect to Co-Pilot"""
        query = request.args.get('q', '')
        return redirect(url_for('co_pilot', query=query))
    
    @app.route('/document-upload-old')
    def document_upload_redirect():
        """Document upload with Ethical AI Assessment"""
        return redirect(url_for('document_upload_route'))
    
    @app.route('/sustainability')
    def sustainability_redirect():
        """Sustainability page redirect to unified dashboard"""
        return redirect(url_for('dashboard'))
    
    @app.route('/sustainability-stories')
    def sustainability_stories_redirect():
        """Stories redirect to story cards"""
        return redirect(url_for('story_cards'))
    
    @app.route('/real-estate-sustainability')
    def real_estate_redirect():
        """Real Estate Sustainability redirect to real estate trend analysis"""
        return redirect(url_for('trend_analysis'))
    
    # Core visualization routes
    @app.route('/trend-analysis')
    def trend_analysis():
        """AI-powered Trend Analysis with Virality Metrics"""
        logger.info("Trend analysis route accessed")
        
        # Get navigation context
        nav_context = get_context_for_template()
        
        # Try to get MongoDB trends
        try:
            from mongo_trends import get_trends
            trends = get_trends(limit=15)
            logger.info(f"Retrieved {len(trends)} trends from MongoDB")
        except Exception as e:
            logger.warning(f"Failed to get trends from MongoDB: {e}")
            trends = []
        
        # Generate mock trends as fallback if needed
        if not trends:
            # Categories with potential virality scores
            categories = [
                {"name": "Climate Action", "base_virality": 85},
                {"name": "Circular Economy", "base_virality": 78},
                {"name": "ESG Reporting", "base_virality": 92},
                {"name": "Green Buildings", "base_virality": 75},
                {"name": "Social Impact", "base_virality": 82}
            ]
            
            # Generate mock trends
            trends = []
            for i in range(15):
                category = categories[i % len(categories)]
                virality = category["base_virality"] + random.uniform(-10, 10)
                
                trends.append({
                    "id": str(i),
                    "name": f"{category['name']} Trend {i+1}",
                    "category": category["name"],
                    "virality_score": min(100, max(50, virality)),
                    "momentum": random.choice(["increasing", "decreasing", "stable"]),
                    "created_at": datetime.now() - timedelta(days=i % 30),
                    "sources": random.randint(3, 15),
                    "social_mentions": random.randint(50, 2000),
                    "news_mentions": random.randint(5, 50)
                })
            logger.info("Using fallback mock trends")
        
        # Ensure trends have all required fields for visualization
        for trend in trends:
            if "virality_score" not in trend:
                trend["virality_score"] = random.uniform(60, 95)
            if "momentum" not in trend:
                trend["momentum"] = random.choice(["increasing", "decreasing", "stable"])
            if "sources" not in trend:
                trend["sources"] = random.randint(3, 15)
            if "social_mentions" not in trend:
                trend["social_mentions"] = random.randint(50, 2000)
            if "news_mentions" not in trend:
                trend["news_mentions"] = random.randint(5, 50)
        
        # Sort trends by virality score
        trends = sorted(trends, key=lambda x: x.get("virality_score", 0), reverse=True)
        
        # Get categories for filtering
        categories = list(set(trend.get("category") for trend in trends))
        
        return render_template(
            'trend_analysis.html',
            trends=trends,
            categories=categories,
            nav_sections=nav_context["nav_sections"],
            user_menu=nav_context["user_menu"],
            active_nav="trend-analysis"
        )
    
    @app.route('/virality-metrics')
    def virality_metrics():
        """Virality Metrics Dashboard - Analyze sustainability trend virality and social impact"""
        # Get navigation context
        nav_context = get_context_for_template()
        
        # Try to get MongoDB trends
        try:
            from mongo_trends import get_trends
            trends = get_trends(limit=20)
            logger.info(f"Retrieved {len(trends)} trends from MongoDB")
        except Exception as e:
            logger.warning(f"Failed to get trends from MongoDB: {e}")
            trends = []
        
        # Generate mock trends as fallback if needed
        if not trends:
            # Generate mock virality data
            trends = []
            categories = ["Climate Action", "Resource Efficiency", "Social Impact", "Governance", "Supply Chain"]
            
            for i in range(20):
                trends.append({
                    "id": str(i),
                    "name": f"Sustainability Trend {i+1}",
                    "category": categories[i % len(categories)],
                    "virality_score": random.uniform(55, 95),
                    "momentum": random.choice(["increasing", "decreasing", "stable"]),
                    "social_mentions": random.randint(100, 5000),
                    "news_mentions": random.randint(10, 100),
                    "industry_adoption": random.uniform(0.1, 0.8),
                    "created_at": datetime.now() - timedelta(days=random.randint(1, 60))
                })
        
        # Format for template
        for trend in trends:
            # Ensure created_at is a datetime
            if isinstance(trend.get('created_at'), str):
                try:
                    trend['created_at'] = datetime.fromisoformat(trend['created_at'])
                except (ValueError, TypeError):
                    trend['created_at'] = datetime.now() - timedelta(days=random.randint(1, 60))
            
            # Ensure all required fields are present
            if "virality_score" not in trend:
                trend["virality_score"] = random.uniform(55, 95)
            if "momentum" not in trend:
                trend["momentum"] = random.choice(["increasing", "decreasing", "stable"])
            if "social_mentions" not in trend:
                trend["social_mentions"] = random.randint(100, 5000)
            if "news_mentions" not in trend:
                trend["news_mentions"] = random.randint(10, 100)
            if "industry_adoption" not in trend:
                trend["industry_adoption"] = random.uniform(0.1, 0.8)
        
        return render_template(
            'virality_metrics.html',
            trends=trends,
            nav_sections=nav_context["nav_sections"],
            user_menu=nav_context["user_menu"],
            active_nav="virality-metrics"
        )
    
    # Debug and utility routes
    @app.route('/debug')
    def debug_route():
        """Debug route to check registered routes and app status"""
        logger.info("Debug route accessed")
        
        # Get all routes
        routes = []
        for rule in app.url_map.iter_rules():
            routes.append({
                "endpoint": rule.endpoint,
                "methods": [m for m in rule.methods if m not in ["HEAD", "OPTIONS"]],
                "path": str(rule)
            })
        
        # Sort routes by endpoint
        routes = sorted(routes, key=lambda r: r["endpoint"])
        
        # Get API status
        try:
            api_status = get_api_status()
        except Exception as e:
            api_status = {"error": str(e)}
        
        # Check MongoDB status
        try:
            from mongo_client import verify_connection
            mongodb_status = verify_connection()
        except Exception as e:
            mongodb_status = {"connected": False, "error": str(e)}
        
        # Get environment variables (excluding sensitive ones)
        env_vars = {}
        for key, value in os.environ.items():
            if not any(sensitive in key.lower() for sensitive in ["key", "secret", "token", "password", "auth"]):
                env_vars[key] = value
        
        # Combine all debug data
        debug_data = {
            "routes": routes,
            "api_status": api_status,
            "mongodb_status": mongodb_status,
            "environment": env_vars,
            "python_version": sys.version,
            "flask_version": flask.__version__,
            "timestamp": datetime.now().isoformat()
        }
        
        # Return JSON if requested
        if request.args.get('format') == 'json':
            return jsonify(debug_data)
        
        # Otherwise render template
        try:
            # Get navigation context
            nav_context = get_context_for_template()
            
            return render_template(
                "debug.html",
                debug_data=debug_data,
                nav_sections=nav_context["nav_sections"],
                user_menu=nav_context["user_menu"],
                active_nav="debug"
            )
        except Exception as e:
            # Fallback to JSON if template is not available
            logger.error(f"Error rendering debug template: {e}")
            return jsonify(debug_data)
    # Return the app after registering all routes
    return app
