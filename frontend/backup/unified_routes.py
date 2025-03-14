"""
Unified Routes Module for SustainaTrend Intelligence Platform

This module adds routes for the unified UI templates with consistent design across all pages.
"""
import json
import logging
import sys
import os
import random
from datetime import datetime, timedelta

# Add the current directory to the path to ensure imports work
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import Flask-related modules
try:
    from flask import Flask, render_template, request, jsonify, redirect, url_for
    import jinja2.exceptions
    from navigation_config import get_context_for_template
except ImportError as e:
    logging.error(f"Error importing Flask modules: {e}")
    raise

logger = logging.getLogger(__name__)

def generate_mock_trends(limit=15):
    """Generate mock sustainability trend data"""
    # Define categories and sample trends
    categories = ["Energy", "Carbon", "Water", "Waste", "Social", "Governance"]
    trend_templates = [
        "Increased {category} efficiency in corporate operations",
        "New {category} regulations impact reporting requirements",
        "{category} innovation drives competitive advantage",
        "Consumer demand for transparent {category} metrics rises",
        "AI-powered {category} optimization gains momentum",
        "Circular economy approaches to {category} management",
        "Investment in {category} technology accelerates",
        "Supply chain {category} tracking becomes standard",
        "ESG frameworks emphasize {category} disclosure",
        "Small businesses adopt {category} best practices"
    ]
    
    trends = []
    for i in range(limit):
        # Select random category and template
        category = random.choice(categories)
        template = random.choice(trend_templates)
        
        # Calculate random stats
        virality_score = random.randint(35, 98)
        growth_rate = random.randint(-15, 45)
        
        # Random date within last 30 days
        days_ago = random.randint(0, 30)
        trend_date = datetime.now() - timedelta(days=days_ago)
        
        # Create trend
        trends.append({
            "id": f"trend-{i+1}",
            "name": template.format(category=category),
            "category": category,
            "description": f"This sustainability trend focuses on {category.lower()} management and innovation. Companies adopting these practices are seeing improved performance and stakeholder engagement.",
            "virality_score": virality_score,
            "growth_rate": growth_rate,
            "date": trend_date,
            "source": random.choice(["Industry Report", "Academic Research", "News Media", "Corporate Disclosure", "Social Media"])
        })
    
    # Sort by virality score
    return sorted(trends, key=lambda x: x["virality_score"], reverse=True)

def register_unified_routes(app):
    """
    Register unified routes for the SustainaTrend Intelligence Platform
    
    Args:
        app: Flask application
    """
    logger.info("Registering unified routes")
    
    # Import navigation configuration for atomic design system
    from navigation_config import get_context_for_template
    
    @app.route('/trend-analysis-unified')
    def trend_analysis_unified():
        """Unified version of the trend analysis page with consistent design"""
        # Get category filter if provided
        category = request.args.get('category', None)
        # Get sort parameter if provided (default to virality)
        sort_by = request.args.get('sort', 'virality')
        
        try:
            # Try to use MongoDB service
            from mongo_trends import get_trends
            
            # Get trend data from MongoDB with filtering
            if category and category != 'all':
                trends = get_trends(category=category, limit=30)
            else:
                trends = get_trends(limit=30)
        except ImportError:
            logger.warning("MongoDB service not available, using fallback data")
            
            # Fall back to mock data if MongoDB isn't available
            try:
                # Try to access mock service from direct_app
                mock_service = app.config.get('mock_service')
                if mock_service:
                    trends = mock_service.get_trends(limit=30)
                else:
                    # If mock service is not available, generate synthetic data
                    trends = generate_mock_trends(limit=30)
            except Exception as e:
                logger.error(f"Error accessing mock service: {str(e)}")
                # Generate synthetic data if all else fails
                trends = generate_mock_trends(limit=30)
        
        # Sort trends based on sort parameter
        if sort_by == 'virality':
            trends = sorted(trends, key=lambda x: x.get('virality_score', 0), reverse=True)
        elif sort_by == 'date':
            trends = sorted(trends, key=lambda x: x.get('date', datetime.now()), reverse=True)
        elif sort_by == 'category':
            trends = sorted(trends, key=lambda x: x.get('category', ''))
        
        # Calculate chart data from the actual trends
        categories = ["Energy", "Carbon", "Water", "Waste", "Social", "Governance"]
        
        # Initialize data for each category with zeros
        category_scores = {cat: 0 for cat in categories}
        category_counts = {cat: 0 for cat in categories}
        
        # Calculate average virality score for each category
        for trend in trends:
            cat = trend.get('category', '')
            if cat and cat in categories and 'virality_score' in trend:
                category_scores[cat] += trend['virality_score']
                category_counts[cat] += 1
        
        # Calculate averages, avoiding division by zero
        chart_data_values = []
        for cat in categories:
            if category_counts[cat] > 0:
                chart_data_values.append(round(category_scores[cat] / category_counts[cat]))
            else:
                chart_data_values.append(0)
        
        # Prepare chart data with dynamic values
        chart_data = {
            "labels": categories,
            "datasets": [{
                "label": "Average Virality Score",
                "data": chart_data_values,
                "backgroundColor": "rgba(76, 175, 80, 0.6)"
            }]
        }
        
        # Generate AI insights based on the actual trend data
        insights = []
        
        # Find the top category
        top_category_index = chart_data_values.index(max(chart_data_values))
        top_category = categories[top_category_index]
        
        # Find the category with largest growth
        growth_by_category = {}
        for trend in trends:
            cat = trend.get('category', '')
            growth = trend.get('growth_rate', 0)
            if cat in categories and growth:
                if cat not in growth_by_category:
                    growth_by_category[cat] = []
                growth_by_category[cat].append(growth)
        
        fastest_growing = "Sustainability" # Default
        highest_growth_rate = 0
        for cat, growths in growth_by_category.items():
            if growths and len(growths) > 0:
                avg_growth = sum(growths) / len(growths)
                if avg_growth > highest_growth_rate:
                    highest_growth_rate = avg_growth
                    fastest_growing = cat
        
        # Create insights
        insights = {
            "top_category": top_category,
            "top_score": max(chart_data_values),
            "fastest_growing": fastest_growing,
            "growth_rate": round(highest_growth_rate)
        }
    
        # Now render the unified template with the data
        logger.info("Rendering unified trend analysis dashboard")
        try:
            return render_template(
                "trend_analysis_unified.html",
                trends=trends,
                trend_chart_data=json.dumps(chart_data),
                category=category or 'all',
                sort=sort_by,
                insights=insights
            )
        except jinja2.exceptions.TemplateNotFound:
            logger.warning("Unified template not found, falling back to original template")
            return redirect(url_for('trend_analysis'))
    
    @app.route('/unified-ai-prompt')
    def unified_ai_prompt():
        """Unified AI prompt interface"""
        return render_template("unified_ai_prompt.html")
        
    @app.route('/atomic-home')
    def atomic_home():
        """Atomic design system home page with 3-column layout"""
        try:
            logger.info("Rendering atomic home page")
            
            # Get navigation context for the template
            nav_context = get_context_for_template()
            
            # Debug the navigation context
            logger.info(f"Navigation context for atomic_home: {nav_context}")
            
            for section in nav_context["nav_sections"]:
                logger.info(f"Section: {section['title']}")
                logger.info(f"Items: {section['items']}")
            
            return render_template(
                "atomic_home.html",
                nav_sections=nav_context["nav_sections"],
                user_menu=nav_context["user_menu"],
                active_nav="home"
            )
        except Exception as e:
            logger.error(f"Error rendering atomic home page: {e}")
            logger.exception(e)
            # In case of error, redirect to the original home page
            return redirect(url_for('home'))
    
    @app.route('/trend-analysis-atomic')
    def trend_analysis_atomic():
        """Atomic design system trend analysis dashboard with 3-column layout"""
        # Get query parameters
        category = request.args.get('category', 'all')
        sort_by = request.args.get('sort', 'virality')
        
        try:
            # Get trend data
            logger.info(f"Fetching trend data with category={category}, sort={sort_by}")
            
            try:
                # Try to get data from MongoDB first
                from mongo_trends import get_trends
                if category and category != 'all':
                    trends = get_trends(category=category, limit=30)
                else:
                    trends = get_trends(limit=30)
                logger.info(f"Retrieved {len(trends)} trends from MongoDB")
            except Exception as e:
                logger.warning(f"MongoDB service not available, using fallback data: {e}")
                # Fallback to mock data
                trends = generate_mock_trends(30)
                logger.info(f"Generated {len(trends)} mock trends as fallback")
            
            # Sort the trends based on the sort parameter
            if sort_by == 'virality':
                trends = sorted(trends, key=lambda x: x.get('virality_score', 0), reverse=True)
            elif sort_by == 'date':
                trends = sorted(trends, key=lambda x: x.get('date', datetime.min), reverse=True)
            elif sort_by == 'category':
                trends = sorted(trends, key=lambda x: x.get('category', ''))
            
            # Calculate average scores by category for chart
            categories = ["Energy", "Carbon", "Water", "Waste", "Social", "Governance"]
            category_scores = {cat: 0 for cat in categories}
            category_counts = {cat: 0 for cat in categories}
            
            chart_data_values = []
            
            # Calculate average score for each category
            for trend in trends:
                cat = trend.get('category')
                score = trend.get('virality_score')
                if cat in categories and score:
                    category_scores[cat] += score
                    category_counts[cat] += 1
            
            # Generate chart data values
            for cat in categories:
                if category_counts[cat] > 0:
                    chart_data_values.append(round(category_scores[cat] / category_counts[cat]))
                else:
                    chart_data_values.append(0)
            
            # Prepare chart data with dynamic values
            chart_data = {
                "labels": categories,
                "datasets": [{
                    "label": "Average Virality Score",
                    "data": chart_data_values,
                    "backgroundColor": "rgba(76, 175, 80, 0.6)"
                }]
            }
            
            # Generate AI insights based on the actual trend data
            insights = []
            
            # Find the top category
            top_category_index = chart_data_values.index(max(chart_data_values))
            top_category = categories[top_category_index]
            
            # Find the category with largest growth
            growth_by_category = {}
            for trend in trends:
                cat = trend.get('category', '')
                growth = trend.get('growth_rate', 0)
                if cat in categories and growth:
                    if cat not in growth_by_category:
                        growth_by_category[cat] = []
                    growth_by_category[cat].append(growth)
            
            fastest_growing = "Sustainability" # Default
            highest_growth_rate = 0
            for cat, growths in growth_by_category.items():
                if growths and len(growths) > 0:
                    avg_growth = sum(growths) / len(growths)
                    if avg_growth > highest_growth_rate:
                        highest_growth_rate = avg_growth
                        fastest_growing = cat
            
            # Create insights
            insights = {
                "top_category": top_category,
                "top_score": max(chart_data_values),
                "fastest_growing": fastest_growing,
                "growth_rate": round(highest_growth_rate)
            }
            
            # Now render the atomic template with the data
            logger.info("Rendering atomic trend analysis dashboard")
            
            # Get navigation context for the template
            nav_context = get_context_for_template()
            
            return render_template(
                "atomic_trend_analysis.html",
                trends=trends,
                trend_chart_data=json.dumps(chart_data),
                category=category or 'all',
                sort=sort_by,
                insights=insights,
                nav_sections=nav_context["nav_sections"],
                user_menu=nav_context["user_menu"],
                active_nav="trends"
            )
        except Exception as e:
            logger.error(f"Error rendering atomic trend analysis template: {e}")
            logger.exception(e)
            # In case of error, redirect to the original template
            return redirect(url_for('trend_analysis'))
    
    @app.route('/analytics-dashboard-atomic')
    def analytics_dashboard_atomic():
        """Atomic design system analytics dashboard with 3-column layout"""
        try:
            logger.info("Rendering atomic analytics dashboard")
            
            # Get navigation context for the template
            nav_context = get_context_for_template()
            
            # In a real implementation, we would pass specific analytics data here
            return render_template(
                "analytics_dashboard_atomic.html",
                nav_sections=nav_context["nav_sections"],
                user_menu=nav_context["user_menu"],
                active_nav="predictive"
            )
        except Exception as e:
            logger.error(f"Error rendering atomic analytics dashboard: {e}")
            logger.exception(e)
            # In case of error, redirect to the original analytics dashboard
            return redirect(url_for('analytics_dashboard'))

    @app.route('/document-upload-atomic')
    def document_upload_atomic():
        """Atomic design system document upload page with 3-column layout"""
        try:
            logger.info("Rendering atomic document upload page")
            
            # Get navigation context for the template
            nav_context = get_context_for_template()
            
            return render_template(
                "atomic_document_upload.html",
                nav_sections=nav_context["nav_sections"],
                user_menu=nav_context["user_menu"],
                active_nav="documents"
            )
        except Exception as e:
            logger.error(f"Error rendering atomic document upload page: {e}")
            logger.exception(e)
            # In case of error, redirect to the original document upload page
            return redirect(url_for('document_upload'))
    
    @app.route('/search-atomic')
    def search_atomic():
        """Atomic design system search page with 3-column layout"""
        # Get query parameter
        query = request.args.get('q', '')
        
        try:
            logger.info(f"Rendering atomic search page with query: {query}")
            
            # Get navigation context for the template
            nav_context = get_context_for_template()
            
            # In a full implementation, we would perform the actual search here
            # and pass the results to the template
            
            return render_template(
                "atomic_search.html",
                query=query,
                nav_sections=nav_context["nav_sections"],
                user_menu=nav_context["user_menu"],
                active_nav="search"
            )
        except Exception as e:
            logger.error(f"Error rendering atomic search page: {e}")
            logger.exception(e)
            # In case of error, redirect to the original search page
            return redirect(url_for('search', q=query))
    
    @app.route('/sustainability-stories-atomic')
    def sustainability_stories_atomic():
        """Atomic design system sustainability stories page with 3-column layout"""
        # Get query parameters
        view_type = request.args.get('view', 'all')
        topic_filter = request.args.get('topic', None)
        
        try:
            logger.info(f"Fetching sustainability stories with view={view_type}, topic={topic_filter}")
            
            # Try to get stories from MongoDB
            try:
                from mongo_stories import get_stories
                
                # Apply filters based on view type
                if view_type == 'published':
                    stories = get_stories(limit=50, skip=0, 
                                         start_date=datetime.now() - timedelta(days=365))
                elif view_type == 'drafts':
                    # In a real implementation, we'd filter by status='draft'
                    stories = get_stories(limit=10, skip=0)
                    # Mark these as drafts for demo purposes
                    for story in stories:
                        story['date'] = None
                        story['status'] = 'draft'
                else:
                    stories = get_stories(limit=50, skip=0)
                
                # Additional topic filtering if specified
                if topic_filter:
                    stories = [s for s in stories if s.get('category') == topic_filter]
                
                logger.info(f"Retrieved {len(stories)} stories from MongoDB")
            except Exception as e:
                logger.warning(f"MongoDB service not available, using fallback data: {e}")
                
                # Generate some mock data for demonstration
                categories = ["Carbon Footprint", "Renewable Energy", "Waste Management", 
                             "Social Responsibility", "Governance", "Water Conservation",
                             "Circular Economy", "Biodiversity", "Supply Chain"]
                
                formats = ["Article", "Report", "Blog Post", "Case Study", "Infographic", "Video"]
                
                story_templates = [
                    "Achieving sustainability goals through {category} initiatives",
                    "How {category} is reshaping business operations",
                    "The future of {category} in corporate sustainability",
                    "Measuring and reporting on {category} metrics",
                    "Stakeholder perspectives on {category}",
                    "Best practices for {category} management",
                    "Regulatory changes affecting {category}",
                    "Innovation in {category} technology",
                    "Cross-industry collaboration on {category}"
                ]
                
                stories = []
                for i in range(20):
                    category = random.choice(categories)
                    template = random.choice(story_templates)
                    
                    # Calculate random dates - some recent, some older
                    days_ago = random.randint(1, 180)
                    story_date = datetime.now() - timedelta(days=days_ago)
                    
                    # Create story object
                    story = {
                        "id": f"story-{i}",
                        "title": template.format(category=category),
                        "category": category,
                        "format": random.choice(formats),
                        "summary": f"This sustainability story explores {category.lower()} initiatives and their impact on business operations and environmental outcomes.",
                        "content": "Full story content would appear here.",
                        "date": story_date if view_type != 'drafts' else None,
                        "status": "published" if view_type != 'drafts' else "draft",
                        "author": "Sustainability Team",
                        "image_url": None,
                        "views": random.randint(10, 5000),
                        "likes": random.randint(0, 500),
                        "comments": random.randint(0, 50)
                    }
                    stories.append(story)
                
                # Filter by view type
                if view_type == 'published':
                    stories = [s for s in stories if s.get('status') == 'published']
                elif view_type == 'drafts':
                    stories = [s for s in stories if s.get('status') == 'draft']
                
                # Additional topic filtering if specified
                if topic_filter:
                    stories = [s for s in stories if s.get('category') == topic_filter]
                
                logger.info(f"Generated {len(stories)} mock stories as fallback")
            
            # Now render the atomic template with the data
            logger.info("Rendering atomic sustainability stories page")
            
            # Get navigation context for the template
            nav_context = get_context_for_template()
            
            return render_template(
                "atomic_sustainability_stories.html",
                stories=stories,
                view=view_type,
                topic=topic_filter,
                nav_sections=nav_context["nav_sections"],
                user_menu=nav_context["user_menu"],
                active_nav="stories"
            )
        except Exception as e:
            logger.error(f"Error rendering atomic sustainability stories template: {e}")
            logger.exception(e)
            # In case of error, redirect to the original template
            return redirect(url_for('sustainability_stories'))
    
    logger.info("Unified routes registered successfully")
    
    return app