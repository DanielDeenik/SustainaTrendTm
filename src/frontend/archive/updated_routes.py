"""
Updated Routes Module for SustainaTrend™ Intelligence Platform

This module consolidates routes from multiple sources into a single, comprehensive
set of routes for the Flask application, prioritizing critical functionality.
"""
import os
import json
import logging
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from functools import wraps

from flask import (
    render_template, 
    jsonify, 
    request, 
    redirect, 
    url_for, 
    Flask, 
    abort, 
    session
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import from other modules as needed
try:
    from direct_app import (
        get_api_status, 
        perform_enhanced_search,
        get_sustainability_metrics,
        cache_result,
        get_ui_suggestions
    )
except ImportError as e:
    logger.warning(f"Failed to import from direct_app.py: {e}")
    # Define fallback functions if imports fail
    def get_api_status():
        """Get the current status of all API services"""
        return {"status": "unknown", "message": "direct_app.py import failed"}
    
    def perform_enhanced_search(query, model="hybrid", max_results=15):
        """Fallback enhanced search function"""
        return {"status": "error", "message": "Search functionality not available"}
    
    def get_sustainability_metrics():
        """Fallback metrics function"""
        return []
    
    def cache_result(expire=300):
        """Fallback cache decorator"""
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                return f(*args, **kwargs)
            return decorated_function
        return decorator
    
    def get_ui_suggestions(query):
        """Fallback UI suggestions function"""
        return []

# Import document processing functionality
try:
    from document_processor import DocumentProcessor
    document_processor = DocumentProcessor()
except ImportError:
    logger.warning("Failed to import DocumentProcessor")
    document_processor = None

def register_routes(app):
    """
    Register all consolidated routes for the SustainaTrend™ Intelligence Platform
    
    Args:
        app: Flask application
    """
    logger.info("Registering updated consolidated routes")
    
    # Register template filters
    @app.template_filter('datetime')
    def filter_datetime(value):
        """Format a datetime object to a friendly string"""
        if isinstance(value, datetime):
            return value.strftime('%Y-%m-%d %H:%M')
        if isinstance(value, str):
            try:
                dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
                return dt.strftime('%Y-%m-%d %H:%M')
            except (ValueError, AttributeError):
                return value
        return value
    
    # Implement monetization routes directly instead of importing
    # to avoid duplicate registration
    
    # Create routes for monetization strategies
    @app.route('/monetization-strategies', methods=['GET'])
    def monetization_strategies_dashboard():
        """Monetization strategies dashboard for sustainability intelligence"""
        logger.info("Monetization strategies dashboard called")
        
        # Include navigation for the template
        from navigation_config import get_context_for_template
        nav_context = get_context_for_template()
        
        # Use analytics_dashboard_dark.html with template_type="monetization"
        logger.info("Using dark themed monetization template")
        return render_template(
            'analytics_dashboard_dark.html',
            page_title="Monetization Strategies Framework",
            template_type="monetization",
            **nav_context  # Include all navigation context
        )
    
    @app.route('/api/monetization-strategy', methods=['POST'])
    def api_monetization_strategy():
        """API endpoint for monetization strategy recommendations"""
        logger.info("Monetization strategy API called")
        
        data = request.json or {}
        document_text = data.get('document_text', '')
        
        if not document_text:
            return jsonify({
                "success": False,
                "error": "No document text provided"
            }), 400
            
        try:
            # Import here to avoid circular imports
            from monetization_strategies import analyze_monetization_opportunities
            results = analyze_monetization_opportunities(document_text)
            
            return jsonify({
                "success": True,
                "results": results
            })
        except Exception as e:
            logger.error(f"Error analyzing monetization opportunities: {str(e)}")
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
            
    logger.info("Direct monetization routes registered successfully")
    
    # Implement document query API routes directly
    @app.route('/api/document-query', methods=['POST'])
    def query_document():
        """
        API endpoint for querying documents using AI
        """
        logger.info("Document query API called")
        
        try:
            # Get request data
            data = request.json
            if not data:
                return jsonify({
                    'success': False,
                    'error': 'No data provided'
                }), 400
                
            query = data.get('query', '')
            document_id = data.get('document_id', '')
            session_id = data.get('session_id', str(uuid.uuid4()))
            
            if not query:
                return jsonify({
                    'success': False,
                    'error': 'No query provided'
                }), 400
                
            if not document_id:
                return jsonify({
                    'success': False,
                    'error': 'No document_id provided'
                }), 400
                
            # Get document from session data
            document_analysis = session.get('document_analysis', {})
            if not document_analysis or document_analysis.get('filename') != document_id:
                return jsonify({
                    'success': False,
                    'error': 'Document not found or session expired'
                }), 404
            
            # Create response
            return jsonify({
                'success': True,
                'response': f"Analysis of document {document_id} for query: {query}",
                'query': query,
                'sources': [],
                'data_available': False,
                'session_id': session_id,
                'timestamp': datetime.now().isoformat()
            })
        
        except Exception as e:
            logger.error(f"Error in document query API: {str(e)}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    logger.info("Direct document query API routes registered successfully")

    # Sustainability Storytelling API endpoint
    @app.route('/api/storytelling', methods=['POST'])
    def api_storytelling():
        """API endpoint for generating AI-driven sustainability stories"""
        logger.info("Storytelling API endpoint called")
        
        data = request.json or {}
        metrics = data.get('metrics', [])
        audience = data.get('audience', 'all')
        topic = data.get('topic', 'general')
        
        if not metrics:
            return jsonify({
                "success": False,
                "error": "No metrics data provided"
            }), 400
            
        try:
            # Generate a sustainability story based on audience type
            story_content = generate_tailored_story(metrics, audience, topic)
            
            # Create story object with generated content
            story = {
                "title": story_content["title"],
                "audience": audience,
                "topic": topic,
                "content": story_content["narrative"],
                "category": story_content["category"],
                "timestamp": datetime.now().isoformat(),
                "metrics_used": len(metrics),
                "recommendations": story_content["recommendations"],
                "id": str(uuid.uuid4())
            }
            
            return jsonify({
                "success": True,
                "story": story
            })
            
        except Exception as e:
            logger.error(f"Error generating storytelling content: {str(e)}")
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    def generate_tailored_story(metrics, audience, topic):
        """
        Generate a tailored sustainability story based on audience type
        
        Args:
            metrics: List of sustainability metrics
            audience: Target audience (executives, operations, investors, etc)
            topic: Topic focus
            
        Returns:
            Dictionary with story components
        """
        # Determine category based on metrics or topic
        categories = ["emissions", "water", "waste", "energy", "social", "governance"]
        category = next((c for c in categories if c in topic.lower()), "emissions")
        
        # Generate audience-specific content
        if audience == "executives":
            title = "Strategic Impact: Carbon Reduction Yields 15% Cost Savings"
            narrative = ("Analysis of carbon emissions data reveals significant strategic advantages from sustainability initiatives. "
                        "Year-over-year comparison shows 15% reduction in operational costs alongside emissions decreases. "
                        "Financial modeling predicts continued ROI growth with additional renewable energy investments.")
            recommendations = ["Expand renewable energy portfolio", "Integrate sustainability metrics into quarterly reports", 
                               "Develop carbon reduction targets for all business units"]
                
        elif audience == "operations":
            title = "Efficiency Gains: Process Optimization Reduces Resource Consumption by 22%"
            narrative = ("Implementation of closed-loop water systems and real-time monitoring has improved operational efficiency. "
                        "Resource consumption metrics indicate 22% reduction in water usage with minimal investment. "
                        "Cross-functional process optimization has created measurable improvements in sustainability KPIs.")
            recommendations = ["Deploy energy-efficient equipment upgrades", "Implement real-time resource monitoring", 
                               "Establish cross-departmental sustainability teams"]
                
        elif audience == "investors":
            title = "ESG Performance: Sustainability Initiatives Drive Long-term Value Creation"
            narrative = ("Comprehensive ESG metrics analysis demonstrates strong correlation between sustainability performance and financial returns. "
                        "Portfolio assessment shows improved risk-adjusted returns in line with sustainability commitments. "
                        "Benchmarking against industry standards reveals competitive advantages in sustainability leadership positions.")
            recommendations = ["Highlight ESG metrics in investor communications", "Quantify financial impact of sustainability initiatives", 
                               "Align capital allocation with long-term sustainability goals"]
        
        else:
            title = f"Sustainability Insights: {topic.capitalize()} Performance Analysis"
            narrative = ("Analysis of sustainability metrics reveals significant progress across environmental indicators. "
                        "Data-driven assessment shows improvements in key performance indicators related to resource efficiency. "
                        "Benchmark comparisons indicate above-average performance in sustainability practices.")
            recommendations = ["Continue monitoring sustainability metrics", "Share best practices across organization", 
                               "Establish targets for further improvement"]
        
        return {
            "title": title,
            "narrative": narrative,
            "category": category,
            "recommendations": recommendations
        }
    
    # Story Cards page
    @app.route('/story-cards')
    def story_cards():
        """AI Storytelling Engine - Data-driven sustainability narratives"""
        logger.info("Story cards route called")
        
        audience = request.args.get('audience', 'all')
        category = request.args.get('category', 'all')
        
        # Include navigation for the template
        from navigation_config import get_context_for_template
        nav_context = get_context_for_template()
        
        # Get enhanced stories
        stories = get_enhanced_stories(audience, category)
        
        # Use the dark themed template for storytelling
        logger.info("Using dark themed storytelling template")
        return render_template(
            "analytics_dashboard_dark.html",
            page_title="Sustainability Storytelling",
            stories=stories,
            audience=audience,
            category=category,
            template_type="storytelling",
            **nav_context  # Include all navigation context
        )
        
    # Helper function for getting enhanced stories
    def get_enhanced_stories(audience='all', category='all'):
        """Helper function for getting enhanced stories"""
        # Default stories if none available
        stories = [
            {
                "title": "Carbon Emissions Reduced by 15% Through Renewable Energy Transition",
                "content": "Analysis shows significant reduction in carbon footprint through strategic investments in solar and wind power. This translates to approximately 500,000 metric tons of CO2 equivalent annually.",
                "audience": "executives",
                "category": "emissions",
                "timestamp": datetime.now() - timedelta(days=2),
                "recommendations": ["Expand renewable energy portfolio", "Integrate emissions tracking in operations", "Invest in carbon offset programs"],
                "id": "story-1"
            },
            {
                "title": "Water Conservation Efforts Show 25% Efficiency Improvement",
                "content": "Implementation of closed-loop water systems and smart monitoring has resulted in notable conservation metrics. Water usage per unit of production has decreased significantly.",
                "audience": "operations",
                "category": "water",
                "timestamp": datetime.now() - timedelta(days=5),
                "recommendations": ["Expand water recycling systems", "Implement real-time monitoring", "Train staff on conservation practices"],
                "id": "story-2"
            },
            {
                "title": "Waste Reduction Initiatives Aligned with Circular Economy Principles",
                "content": "Material flow analysis reveals improved resource efficiency and waste elimination. Processing byproducts are now being reintroduced into the production cycle.",
                "audience": "all",
                "category": "waste",
                "timestamp": datetime.now() - timedelta(days=1),
                "recommendations": ["Implement circular design principles", "Establish supplier waste reduction programs", "Set waste diversion targets"],
                "id": "story-3"
            },
            {
                "title": "ESG Performance Drives 12% Increase in Stakeholder Engagement",
                "content": "Comprehensive analysis of investor communications shows increased engagement following enhanced ESG reporting. Structured interviews with stakeholders indicate improved brand perception based on sustainability initiatives.",
                "audience": "investors",
                "category": "governance",
                "timestamp": datetime.now() - timedelta(days=4),
                "recommendations": ["Enhance ESG reporting framework", "Quantify financial impact of sustainability", "Align governance with sustainability principles"],
                "id": "story-4"
            }
        ]
        
        # Generate additional dynamic stories based on audience if filtering
        if audience != 'all' and len([s for s in stories if s['audience'] == audience]) < 2:
            # Create a dynamic, audience-specific story
            story_content = generate_tailored_story(
                metrics=[{"name": "Example Metric", "value": 150}], 
                audience=audience, 
                topic=category if category != 'all' else 'sustainability'
            )
            
            dynamic_story = {
                "title": story_content["title"],
                "content": story_content["narrative"],
                "audience": audience,
                "category": story_content["category"],
                "timestamp": datetime.now(),
                "recommendations": story_content["recommendations"],
                "id": f"dynamic-story-{uuid.uuid4()}"
            }
            
            stories.append(dynamic_story)
        
        # Filter by audience if specified
        if audience != 'all':
            stories = [s for s in stories if s['audience'] == audience or s['audience'] == 'all']
            
        # Filter by category if specified
        if category != 'all':
            stories = [s for s in stories if s['category'] == category]
            
        return stories
    
    # Home page
    @app.route('/')
    def home():
        """Home AI Trends Feed - Main entry point with sustainability trends"""
        logger.info("Home route called")
        
        # Include navigation for the template
        from navigation_config import get_context_for_template
        nav_context = get_context_for_template()
        
        # Get current API status for display
        api_status = get_api_status()
        
        # Use finchat_dark_dashboard.html for consistent dark theme UI
        logger.info("Using Finchat dark dashboard template")
        return render_template(
            "finchat_dark_dashboard.html", 
            page_title="SustainaTrend™ Intelligence Platform",
            api_status=api_status,
            **nav_context  # Include all navigation context
        )
    
    # Dashboard page
    @app.route('/dashboard')
    def dashboard():
        """Unified dashboard page combining sustainability metrics and key indicators"""
        logger.info("Dashboard route called")
        
        # Include navigation for the template
        from navigation_config import get_context_for_template
        nav_context = get_context_for_template()
        
        # Get sustainability metrics
        metrics = get_sustainability_metrics()
        
        # Format metrics for dashboard display
        formatted_metrics = json.dumps(metrics, default=lambda o: o.isoformat() if isinstance(o, datetime) else str(o))
        
        # Use the dark themed dashboard
        logger.info("Using Finchat dark dashboard template")
        return render_template(
            "finchat_dark_dashboard.html", 
            page_title="Sustainability Intelligence Dashboard",
            metrics=metrics,
            metrics_json=formatted_metrics,
            **nav_context  # Include all navigation context
        )
    
    # API metrics endpoint
    @app.route('/api/metrics')
    def api_metrics():
        """API endpoint for metrics data"""
        logger.info("API metrics route called")
        
        # Get sustainability metrics
        metrics = get_sustainability_metrics()
        
        # Add timestamp for cache management
        response_data = {
            "metrics": metrics,
            "timestamp": datetime.now().isoformat(),
            "count": len(metrics)
        }
        
        # Convert datetime objects to ISO format for JSON serialization
        class DateTimeEncoder(json.JSONEncoder):
            def default(self, o):
                if isinstance(o, datetime):
                    return o.isoformat()
                return super().default(o)
        
        return app.response_class(
            response=json.dumps(response_data, cls=DateTimeEncoder),
            status=200,
            mimetype='application/json'
        )
    
    # Search route
    @app.route('/search')
    def search():
        """Search interface with AI-powered results"""
        logger.info("Search route called")
        query = request.args.get('query', '')
        model = request.args.get('model', 'hybrid')
        
        # Include navigation for the template
        from navigation_config import get_context_for_template
        nav_context = get_context_for_template()
        
        # Use dark themed search template via analytics dashboard
        logger.info("Using dark themed search template")
        return render_template(
            "analytics_dashboard_dark.html",
            page_title="Sustainability Intelligence Search",
            query=query,
            model=model,
            template_type="copilot",  # Use Co-Pilot UI for search
            **nav_context  # Include all navigation context
        )
    
    # API search suggestions endpoint
    @app.route("/api/omniparser/suggestions", methods=["GET"])
    def omniparser_suggestions_flask():
        """API endpoint for dynamic search suggestions"""
        logger.info("Search suggestions API called")
        query = request.args.get('query', '')
        suggestions = get_ui_suggestions(query)
        return jsonify({"suggestions": suggestions})
    
    # Real-time search API
    @app.route("/api/realtime-search")
    def api_realtime_search():
        """API endpoint for real-time search results"""
        logger.info("Realtime search API called")
        query = request.args.get('query', '')
        model = request.args.get('model', 'hybrid')
        max_results = int(request.args.get('max_results', 15))
        
        # If query is empty, return empty results
        if not query:
            return jsonify({
                "results": [],
                "query": "",
                "count": 0,
                "model": model
            })
        
        # Perform search
        search_results = perform_enhanced_search(query, model, max_results)
        
        return jsonify(search_results)
    
    # Trend analysis page
    @app.route('/trend-analysis')
    def trend_analysis():
        """
        AI-powered sustainability trend analysis page
        Shows trends, predictions, and insights for sustainability metrics
        """
        logger.info("Trend analysis route called")
        category = request.args.get('category', 'all')
        sort = request.args.get('sort', 'virality')
        
        # Include navigation for the template
        from navigation_config import get_context_for_template
        nav_context = get_context_for_template()
        
        # Get trend data for the template
        try:
            from mongo_trends import get_trends
            trends = get_trends(limit=50)
        except (ImportError, Exception) as e:
            logger.warning(f"Failed to get trends from MongoDB: {e}")
            # Use fallback trends
            trends = [
                {
                    "name": "Carbon Neutrality Pledges",
                    "category": "Climate Action",
                    "virality_score": 87,
                    "sentiment": 0.78,
                    "mentions": 1458,
                    "timestamp": datetime.now() - timedelta(days=3)
                },
                {
                    "name": "ESG Reporting Standards",
                    "category": "Governance",
                    "virality_score": 92,
                    "sentiment": 0.65,
                    "mentions": 2104,
                    "timestamp": datetime.now() - timedelta(days=1)
                },
                {
                    "name": "Circular Economy Initiatives",
                    "category": "Resource Efficiency",
                    "virality_score": 76,
                    "sentiment": 0.81,
                    "mentions": 873,
                    "timestamp": datetime.now() - timedelta(days=5)
                }
            ]
        
        # Use the dark themed template
        logger.info("Using dark themed trend analysis template")
        return render_template(
            "realestate_trend_analysis_dark.html", 
            page_title="Sustainability Trend Analysis",
            category=category,
            sort=sort,
            trends=trends,
            **nav_context  # Include all navigation context
        )
    
    # API trends endpoint
    @app.route('/api/trends')
    def api_trends():
        """API endpoint for sustainability trend data for React dashboard"""
        logger.info("API trends route called")
        
        # Convert various datatypes to JSON-serializable formats
        def convert_numeric_types(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            if isinstance(obj, (int, float)):
                return obj
            return str(obj)
            
        try:
            from mongo_trends import get_trends
            trends = get_trends(limit=50)
        except (ImportError, Exception) as e:
            logger.warning(f"Failed to get trends from MongoDB: {e}")
            # Use fallback trends
            trends = [
                {
                    "name": "Carbon Neutrality Pledges",
                    "category": "Climate Action",
                    "virality_score": 87,
                    "sentiment": 0.78,
                    "mentions": 1458,
                    "timestamp": datetime.now() - timedelta(days=3)
                },
                {
                    "name": "ESG Reporting Standards",
                    "category": "Governance",
                    "virality_score": 92,
                    "sentiment": 0.65,
                    "mentions": 2104,
                    "timestamp": datetime.now() - timedelta(days=1)
                },
                {
                    "name": "Circular Economy Initiatives",
                    "category": "Resource Efficiency",
                    "virality_score": 76,
                    "sentiment": 0.81,
                    "mentions": 873,
                    "timestamp": datetime.now() - timedelta(days=5)
                }
            ]
            
        return jsonify({
            "trends": trends,
            "count": len(trends),
            "timestamp": datetime.now().isoformat()
        })
    
    # Debug route
    @app.route('/debug')
    def debug_route():
        """Debug route to check registered routes and app status"""
        logger.info("Debug route called")
        import platform
        import flask
        
        # Get Python and Flask version
        python_version = platform.python_version()
        flask_version = flask.__version__
        
        routes = sorted([str(rule) for rule in app.url_map.iter_rules()])
        
        # Check MongoDB connection if available
        mongo_status = "Not tested"
        try:
            from mongo_client import verify_connection
            if verify_connection():
                mongo_status = "Connected"
            else:
                mongo_status = "Failed to connect"
        except ImportError:
            mongo_status = "MongoDB client not available"
        
        # Include navigation for the template
        from navigation_config import get_context_for_template
        nav_context = get_context_for_template()
        
        # Use the dark themed template for debug info
        logger.info("Using dark themed debug template")
        return render_template(
            'analytics_dashboard_dark.html', 
            routes=routes,
            python_version=python_version,
            flask_version=flask_version,
            mongo_status=mongo_status,
            api_status=get_api_status(),
            template_type="debug",
            page_title="Debug - Registered Routes",
            **nav_context  # Include all navigation context
        )
    
    # Document upload page
    @app.route('/document-upload')
    def document_upload():
        """Document upload page for sustainability document analysis"""
        logger.info("Document upload route called")
        
        # Include navigation for the template
        from navigation_config import get_context_for_template
        nav_context = get_context_for_template()
        
        # Use analytics_dashboard_dark.html with template_type="documents"
        logger.info("Using dark themed document upload template")
        return render_template(
            "analytics_dashboard_dark.html",
            page_title="Sustainability Document Upload & Analysis",
            template_type="documents",
            **nav_context  # Include all navigation context
        )
        
    # Document upload processing
    @app.route('/upload-sustainability-document', methods=['POST'])
    def upload_sustainability_document():
        """Process uploaded sustainability document"""
        logger.info("Document upload processing route called")
        
        # Check if document processor is available
        if document_processor is None:
            return jsonify({
                "status": "error",
                "message": "Document processing functionality is not available"
            }), 500
        
        # Check if the post request has the file part
        if 'document' not in request.files:
            return jsonify({
                "status": "error",
                "message": "No document part in the request"
            }), 400
            
        file = request.files['document']
        
        # If user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            return jsonify({
                "status": "error",
                "message": "No selected file"
            }), 400
            
        # Check if the file is allowed
        allowed_extensions = {'pdf', 'docx', 'txt'}
        if '.' not in file.filename or file.filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
            return jsonify({
                "status": "error",
                "message": f"File type not allowed. Please upload {', '.join(allowed_extensions)}"
            }), 400
            
        # Save the file to upload directory
        uploads_dir = os.path.join(os.getcwd(), 'frontend', 'uploads')
        
        # Create directory if it doesn't exist
        if not os.path.exists(uploads_dir):
            os.makedirs(uploads_dir)
            
        # Generate unique filename
        timestamp = int(time.time())
        extension = file.filename.rsplit('.', 1)[1].lower()
        filename = f"{timestamp}.{extension}"
        file_path = os.path.join(uploads_dir, filename)
        
        # Save file
        file.save(file_path)
        
        # Process document
        try:
            result = document_processor.process_document(file_path)
            
            # Redirect to analysis page
            return jsonify({
                "status": "success",
                "message": "Document uploaded successfully",
                "document_id": filename,
                "redirect_url": url_for('analyze_sustainability_document', document_id=filename)
            })
            
        except Exception as e:
            logger.error(f"Error processing document: {e}")
            return jsonify({
                "status": "error",
                "message": f"Error processing document: {str(e)}"
            }), 500
    
    # Document analysis page
    @app.route('/analyze-sustainability-document/<document_id>')
    def analyze_sustainability_document(document_id):
        """Analyze uploaded sustainability document"""
        logger.info(f"Document analysis route called for document: {document_id}")
        
        # File path for the document
        uploads_dir = os.path.join(os.getcwd(), 'frontend', 'uploads')
        file_path = os.path.join(uploads_dir, document_id)
        
        # Include navigation for the template
        from navigation_config import get_context_for_template
        nav_context = get_context_for_template()
        
        # Check if file exists
        if not os.path.exists(file_path):
            logger.error(f"Document not found: {file_path}")
            return render_template(
                "analytics_dashboard_dark.html",
                error_message="Document not found. It may have been deleted or the ID is invalid.",
                template_type="debug",
                page_title="Document Not Found",
                **nav_context
            ), 404
        
        # Check if document processor is available
        if document_processor is None:
            return render_template(
                "analytics_dashboard_dark.html",
                error_message="Document processing functionality is not available",
                template_type="debug",
                page_title="Processing Error",
                **nav_context
            ), 500
        
        # Process document
        try:
            result = document_processor.process_document(file_path)
            
            # For demo purposes, add document_id to result
            result['document_id'] = document_id
            
            # Use the dark themed template for document analysis
            logger.info("Using dark themed document analysis template")
            return render_template(
                "analytics_dashboard_dark.html",
                result=result,
                document_id=document_id,
                template_type="documents",
                page_title="Sustainability Document Analysis",
                **nav_context  # Include all navigation context
            )
            
        except Exception as e:
            logger.error(f"Error analyzing document: {e}")
            return render_template(
                "analytics_dashboard_dark.html",
                error_message=f"Error analyzing document: {str(e)}",
                template_type="debug",
                page_title="Analysis Error",
                **nav_context
            ), 500
    
    # API status dashboard
    @app.route("/api-status")
    def api_status_dashboard():
        """API Status Dashboard - Check the status of API services"""
        logger.info("API status dashboard route called")
        
        api_status = get_api_status()
        
        # Use the dark themed template for API status
        logger.info("Using dark themed API status template")
        
        # Include navigation for the template
        from navigation_config import get_context_for_template
        nav_context = get_context_for_template()
        
        return render_template(
            "analytics_dashboard_dark.html",
            api_status=api_status,
            template_type="debug",
            page_title="API Status Dashboard",
            **nav_context  # Include all navigation context
        )
    
    # Real Estate Sustainability page
    @app.route('/real-estate-sustainability')
    def real_estate_sustainability():
        """Real Estate Sustainability - Specialized insights for the real estate sector"""
        logger.info("Real estate sustainability route called")
        
        # Include navigation for the template
        from navigation_config import get_context_for_template
        nav_context = get_context_for_template()
        
        # Get trend data for the template
        try:
            from mongo_trends import get_trends
            trends = get_trends(limit=50)
        except (ImportError, Exception) as e:
            logger.warning(f"Failed to get trends from MongoDB: {e}")
            # Use fallback trends
            trends = [
                {
                    "name": "Green Building Certifications",
                    "category": "Real Estate",
                    "virality_score": 83,
                    "sentiment": 0.75,
                    "mentions": 1289,
                    "timestamp": datetime.now() - timedelta(days=2)
                },
                {
                    "name": "Net Zero Buildings",
                    "category": "Real Estate",
                    "virality_score": 90,
                    "sentiment": 0.82,
                    "mentions": 1965,
                    "timestamp": datetime.now() - timedelta(days=1)
                },
                {
                    "name": "Sustainable Urban Planning",
                    "category": "Real Estate",
                    "virality_score": 79,
                    "sentiment": 0.77,
                    "mentions": 943,
                    "timestamp": datetime.now() - timedelta(days=4)
                }
            ]
        
        # Use the dark themed template
        logger.info("Using dark themed real estate sustainability template")
        return render_template(
            "realestate_trend_analysis_dark.html",
            page_title="Real Estate Sustainability",
            trends=trends,
            **nav_context  # Include all navigation context
        )
        
    # Register error handlers
    @app.errorhandler(404)
    def page_not_found(e):
        """Handle 404 errors"""
        logger.warning(f"404 error: {request.path}")
        
        # Include navigation for the template
        from navigation_config import get_context_for_template
        nav_context = get_context_for_template()
        
        # Use the dark themed template for error pages
        logger.info("Using dark themed error template")
        return render_template(
            'analytics_dashboard_dark.html',
            error_message="The page you're looking for doesn't exist.",
            template_type="debug",  # Use debug layout for errors
            page_title="Page Not Found",
            **nav_context  # Include all navigation context
        ), 404
    
    logger.info("All routes registered successfully")