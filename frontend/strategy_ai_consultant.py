"""
Strategy AI Consultant Module for SustainaTrend™

This module provides AI-powered strategic consulting capabilities for sustainability trends,
functioning as an automated management consultant that analyzes trends, generates strategic
recommendations, and creates comprehensive strategy documents.

Key features:
1. Framework-based trend analysis (STEPPS, Porter's Five Forces, SWOT, PESTEL)
2. Strategic recommendations generation
3. Implementation planning
4. Opportunity and threat identification
5. Strategy document generation
"""

import os
import json
import re
import logging
import random
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple, Union

# AI providers
try:
    import openai
except ImportError:
    logging.warning("OpenAI module not available, using fallback")
    openai = None

try:
    import google.generativeai as genai
except ImportError:
    logging.warning("Google Generative AI module not available, using fallback")
    genai = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize AI providers
def initialize_ai_providers():
    """Initialize AI providers based on available API keys"""
    ai_providers = []
    
    # Initialize OpenAI
    if os.environ.get("OPENAI_API_KEY"):
        try:
            openai.api_key = os.environ.get("OPENAI_API_KEY")
            ai_providers.append("openai")
            logger.info("OpenAI initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing OpenAI: {e}")
    
    # Initialize Google Gemini
    if os.environ.get("GEMINI_API_KEY"):
        try:
            genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
            ai_providers.append("gemini")
            logger.info("Google Gemini initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing Google Gemini: {e}")
    
    return ai_providers

# Check available AI providers
AI_PROVIDERS = initialize_ai_providers()

# Analysis frameworks
FRAMEWORKS = {
    "STEPPS": {
        "name": "STEPPS Virality Framework",
        "description": "Framework for analyzing why certain topics gain traction and spread virally",
        "components": [
            "Social Currency", "Triggers", "Emotion", "Public", "Practical Value", "Stories"
        ]
    },
    "Porter's Five Forces": {
        "name": "Porter's Five Forces",
        "description": "Framework for analyzing competitive dynamics and market positioning",
        "components": [
            "Threat of New Entrants", "Bargaining Power of Suppliers", 
            "Bargaining Power of Buyers", "Threat of Substitutes", "Industry Rivalry"
        ]
    },
    "SWOT": {
        "name": "SWOT Analysis",
        "description": "Framework for identifying internal strengths and weaknesses, and external opportunities and threats",
        "components": [
            "Strengths", "Weaknesses", "Opportunities", "Threats"
        ]
    },
    "PESTEL": {
        "name": "PESTEL Analysis",
        "description": "Framework for examining external macro-environmental factors",
        "components": [
            "Political", "Economic", "Social", "Technological", "Environmental", "Legal"
        ]
    }
}

def analyze_trend(trend_name: str, industry: str = "General", timeframe: str = "medium", 
                 frameworks: List[str] = None) -> Dict[str, Any]:
    """
    Analyze a sustainability trend or challenge using AI-powered strategic analysis
    
    Args:
        trend_name: Name or description of the trend to analyze
        industry: Industry context for the analysis
        timeframe: Timeframe for the analysis (short, medium, long)
        frameworks: List of frameworks to use in the analysis
        
    Returns:
        Dictionary with analysis results
    """
    logger.info(f"Analyzing trend: {trend_name} for industry: {industry}")
    
    # Default frameworks if none provided
    if not frameworks:
        frameworks = ["STEPPS", "Porter's Five Forces"]
    
    # Use available AI provider
    if "openai" in AI_PROVIDERS:
        analysis = analyze_trend_with_openai(trend_name, industry, timeframe, frameworks)
    elif "gemini" in AI_PROVIDERS:
        analysis = analyze_trend_with_gemini(trend_name, industry, timeframe, frameworks)
    else:
        # Fallback to mock analysis
        analysis = generate_mock_analysis(trend_name, industry, timeframe, frameworks)
        
    return analysis

def analyze_trend_with_openai(trend_name: str, industry: str, timeframe: str, 
                             frameworks: List[str]) -> Dict[str, Any]:
    """
    Analyze trend using OpenAI
    
    Args:
        trend_name: Trend to analyze
        industry: Industry context
        timeframe: Analysis timeframe
        frameworks: Frameworks to use
        
    Returns:
        Analysis results
    """
    logger.info(f"Using OpenAI to analyze trend: {trend_name}")
    
    # Timeframe mapping
    timeframe_map = {
        "short": "1 year", 
        "medium": "3 years", 
        "long": "5+ years"
    }
    
    # Construct the prompt for OpenAI using atom-of-thought prompt engineering
    prompt = f"""
    As an AI Management Consultant specializing in sustainability strategy, perform a comprehensive analysis of the sustainability trend/challenge: '{trend_name}'
    
    Industry Context: {industry}
    Timeframe: {timeframe_map.get(timeframe, "3 years")}
    
    Use the following atom-of-thought approach to thoroughly analyze each component:
    
    1. Executive Summary:
       - Describe the trend/challenge and its significance in the sustainability landscape
       - Assess the current maturity and adoption of this trend in the {industry} industry
       - Evaluate the strategic implications for businesses within a {timeframe_map.get(timeframe, "3 years")} timeframe
       - Highlight the critical factors that make this trend strategically important
    
    2. Strategic Recommendations:
       - Provide 3-5 specific, actionable recommendations
       - For each recommendation:
         * Describe the recommendation in detail
         * Explain why it's strategically important
         * Identify which stakeholders would be responsible for implementation
         * Note any prerequisites or dependencies for successful implementation
    
    3. Strategic Actions:
       - Outline 3-5 concrete implementation steps
       - For each action:
         * Describe the specific steps required
         * Suggest a realistic timeline for implementation
         * Identify potential resource requirements
         * Note any critical success factors
    
    4. Opportunities:
       - Identify 3-5 specific opportunities presented by this trend
       - For each opportunity:
         * Describe the opportunity in detail
         * Explain how it creates value
         * Assess its potential impact on the business
         * Note any first-mover advantages or timing considerations
    
    5. Threats:
       - Identify 3-5 specific threats or risks associated with this trend
       - For each threat:
         * Describe the threat in detail
         * Assess its potential impact
         * Suggest mitigation strategies
         * Identify early warning indicators
    
    6. Framework Analysis:
    """
    
    # Add framework-specific instructions to the prompt
    for framework in frameworks:
        if framework in FRAMEWORKS:
            prompt += f"\n    - {FRAMEWORKS[framework]['name']}: {FRAMEWORKS[framework]['description']}"
    
    prompt += """
    
    Format your response as a valid JSON object with the following structure:
    {
        "trend_name": "Name of the trend/challenge",
        "industry": "Industry analyzed",
        "timeframe": "Timeframe analyzed",
        "summary": "Executive summary paragraph",
        "recommendations": ["Recommendation 1", "Recommendation 2", ...],
        "strategic_actions": ["Action 1", "Action 2", ...],
        "opportunities": ["Opportunity 1", "Opportunity 2", ...],
        "threats": ["Threat 1", "Threat 2", ...],
        "assessment": {
            "Framework Name": {
                "Component 1": "Analysis for component 1",
                "Component 2": "Analysis for component 2",
                ...
            }
        }
    }
    """
    
    try:
        # Call OpenAI API
        response = openai.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "You are an AI Management Consultant specializing in sustainability strategies."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2500,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        
        # Extract and parse the response
        response_text = response.choices[0].message.content
        
        # Try to extract JSON from the response
        json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
        if json_match:
            response_text = json_match.group(1)
        else:
            # Try to find JSON without code blocks
            json_match = re.search(r'(\{.*\})', response_text, re.DOTALL)
            if json_match:
                response_text = json_match.group(1)
        
        # Parse JSON
        analysis = json.loads(response_text)
        
        # Ensure required fields are present
        required_fields = ["trend_name", "industry", "timeframe", "summary", 
                           "recommendations", "strategic_actions", "opportunities", 
                           "threats", "assessment"]
        
        for field in required_fields:
            if field not in analysis:
                analysis[field] = "Not provided" if field in ["trend_name", "industry", 
                                                            "timeframe", "summary"] else []
        
        return analysis
    
    except Exception as e:
        logger.error(f"Error analyzing trend with OpenAI: {e}")
        return generate_mock_analysis(trend_name, industry, timeframe, frameworks)

def analyze_trend_with_gemini(trend_name: str, industry: str, timeframe: str, 
                             frameworks: List[str]) -> Dict[str, Any]:
    """
    Analyze trend using Google Gemini
    
    Args:
        trend_name: Trend to analyze
        industry: Industry context
        timeframe: Analysis timeframe
        frameworks: Frameworks to use
        
    Returns:
        Analysis results
    """
    logger.info(f"Using Google Gemini to analyze trend: {trend_name}")
    
    # Timeframe mapping
    timeframe_map = {
        "short": "1 year", 
        "medium": "3 years", 
        "long": "5+ years"
    }
    
    # Construct the prompt for Gemini using atom-of-thought prompt engineering
    prompt = f"""
    As an AI Management Consultant specializing in sustainability strategy, perform a comprehensive analysis of the sustainability trend/challenge: '{trend_name}'
    
    Industry Context: {industry}
    Timeframe: {timeframe_map.get(timeframe, "3 years")}
    
    Use the following atom-of-thought approach to thoroughly analyze each component:
    
    1. Executive Summary:
       - Describe the trend/challenge and its significance in the sustainability landscape
       - Assess the current maturity and adoption of this trend in the {industry} industry
       - Evaluate the strategic implications for businesses within a {timeframe_map.get(timeframe, "3 years")} timeframe
       - Highlight the critical factors that make this trend strategically important
    
    2. Strategic Recommendations:
       - Provide 3-5 specific, actionable recommendations
       - For each recommendation:
         * Describe the recommendation in detail
         * Explain why it's strategically important
         * Identify which stakeholders would be responsible for implementation
         * Note any prerequisites or dependencies for successful implementation
    
    3. Strategic Actions:
       - Outline 3-5 concrete implementation steps
       - For each action:
         * Describe the specific steps required
         * Suggest a realistic timeline for implementation
         * Identify potential resource requirements
         * Note any critical success factors
    
    4. Opportunities:
       - Identify 3-5 specific opportunities presented by this trend
       - For each opportunity:
         * Describe the opportunity in detail
         * Explain how it creates value
         * Assess its potential impact on the business
         * Note any first-mover advantages or timing considerations
    
    5. Threats:
       - Identify 3-5 specific threats or risks associated with this trend
       - For each threat:
         * Describe the threat in detail
         * Assess its potential impact
         * Suggest mitigation strategies
         * Identify early warning indicators
    
    6. Framework Analysis:
    """
    
    # Add framework-specific instructions to the prompt
    for framework in frameworks:
        if framework in FRAMEWORKS:
            prompt += f"\n    - {FRAMEWORKS[framework]['name']}: {FRAMEWORKS[framework]['description']}"
    
    prompt += """
    
    Format your response as a valid JSON object with the following structure:
    {
        "trend_name": "Name of the trend/challenge",
        "industry": "Industry analyzed",
        "timeframe": "Timeframe analyzed",
        "summary": "Executive summary paragraph",
        "recommendations": ["Recommendation 1", "Recommendation 2", ...],
        "strategic_actions": ["Action 1", "Action 2", ...],
        "opportunities": ["Opportunity 1", "Opportunity 2", ...],
        "threats": ["Threat 1", "Threat 2", ...],
        "assessment": {
            "Framework Name": {
                "Component 1": "Analysis for component 1",
                "Component 2": "Analysis for component 2",
                ...
            }
        }
    }
    """
    
    try:
        # Get the best available model
        model = genai.GenerativeModel('gemini-pro')
        
        # Call Gemini API
        response = model.generate_content(prompt)
        
        # Extract and parse the response
        response_text = response.text
        
        # Try to extract JSON from the response
        json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
        if json_match:
            response_text = json_match.group(1)
        else:
            # Try to find JSON without code blocks
            json_match = re.search(r'(\{.*\})', response_text, re.DOTALL)
            if json_match:
                response_text = json_match.group(1)
        
        # Parse JSON
        analysis = json.loads(response_text)
        
        # Ensure required fields are present
        required_fields = ["trend_name", "industry", "timeframe", "summary", 
                           "recommendations", "strategic_actions", "opportunities", 
                           "threats", "assessment"]
        
        for field in required_fields:
            if field not in analysis:
                analysis[field] = "Not provided" if field in ["trend_name", "industry", 
                                                            "timeframe", "summary"] else []
        
        return analysis
    
    except Exception as e:
        logger.error(f"Error analyzing trend with Gemini: {e}")
        return generate_mock_analysis(trend_name, industry, timeframe, frameworks)

def integrate_trend_analytics(analysis: Dict[str, Any], 
                            frameworks: List[str]) -> Dict[str, Any]:
    """
    Integrate trend analytics from other modules into the analysis
    
    Args:
        analysis: Existing analysis
        frameworks: Frameworks to use
        
    Returns:
        Enhanced analysis with integrated trend analytics
    """
    try:
        # Import only when needed to avoid circular imports
        from trend_virality_benchmarking import analyze_trend_stepps, analyze_trend_competitive_benchmark
        
        trend_name = analysis.get("trend_name", "")
        
        # If STEPPS framework is requested, enhance with trend virality
        if "STEPPS" in frameworks and trend_name:
            stepps_analysis = analyze_trend_stepps(trend_name)
            
            # Update the assessment with STEPPS data
            if "assessment" not in analysis:
                analysis["assessment"] = {}
            
            analysis["assessment"]["STEPPS"] = {
                "Social Currency": stepps_analysis["components"]["social_currency"]["recommendation"],
                "Triggers": stepps_analysis["components"]["triggers"]["recommendation"],
                "Emotion": stepps_analysis["components"]["emotion"]["recommendation"],
                "Public": stepps_analysis["components"]["public"]["recommendation"],
                "Practical Value": stepps_analysis["components"]["practical_value"]["recommendation"],
                "Stories": stepps_analysis["components"]["stories"]["recommendation"]
            }
            
        # If Porter's Five Forces is requested, enhance with competitive benchmark
        if "Porter's Five Forces" in frameworks and trend_name:
            benchmark_analysis = analyze_trend_competitive_benchmark(trend_name)
            
            # Update the assessment with benchmark data
            if "assessment" not in analysis:
                analysis["assessment"] = {}
                
            if "Porter's Five Forces" not in analysis["assessment"]:
                analysis["assessment"]["Porter's Five Forces"] = {}
                
            for force in FRAMEWORKS["Porter's Five Forces"]["components"]:
                if force not in analysis["assessment"]["Porter's Five Forces"]:
                    analysis["assessment"]["Porter's Five Forces"][force] = f"Analysis based on competitive benchmark for {force}."
    
    except Exception as e:
        logger.error(f"Error integrating trend analytics: {e}")
        
    return analysis

def generate_mock_analysis(trend_name: str, industry: str, timeframe: str, 
                          frameworks: List[str]) -> Dict[str, Any]:
    """
    Generate mock strategic analysis when AI services are unavailable
    
    Args:
        trend_name: Trend to analyze
        industry: Industry context
        timeframe: Analysis timeframe
        frameworks: Frameworks to use
        
    Returns:
        Mock analysis results
    """
    logger.warning(f"Generating mock analysis for trend: {trend_name}")
    
    # Timeframe mapping
    timeframe_map = {
        "short": "1 year", 
        "medium": "3 years", 
        "long": "5+ years"
    }
    
    # Generate mock analysis
    analysis = {
        "trend_name": trend_name,
        "industry": industry,
        "timeframe": timeframe_map.get(timeframe, "3 years"),
        "summary": f"This is a strategic analysis of the sustainability trend '{trend_name}' for the {industry} industry over a {timeframe_map.get(timeframe, '3 years')} timeframe. This trend represents a significant opportunity for organizations to address environmental challenges while creating business value.",
        "recommendations": [
            f"Develop a comprehensive {trend_name} strategy aligned with business objectives",
            f"Invest in technologies that enable better measurement and reporting of {trend_name}",
            f"Collaborate with industry peers on {trend_name} standards and best practices",
            f"Train staff on {trend_name} implementation and benefits"
        ],
        "strategic_actions": [
            f"Conduct a baseline assessment of current {trend_name} performance",
            "Form a cross-functional team to lead implementation",
            "Develop key performance indicators to track progress",
            "Establish reporting mechanisms for stakeholders"
        ],
        "opportunities": [
            "Enhanced brand reputation and market positioning",
            "Operational cost savings through increased efficiency",
            "Attraction and retention of sustainability-conscious talent",
            "Potential for new product/service innovations"
        ],
        "threats": [
            "Increasing regulatory requirements and compliance costs",
            "Changing customer expectations requiring rapid adaptation",
            "Competitive pressure from sustainability leaders",
            "Potential supply chain disruptions during transition"
        ],
        "assessment": {}
    }
    
    # Add mock framework assessments
    for framework in frameworks:
        if framework in FRAMEWORKS:
            framework_data = {}
            for component in FRAMEWORKS[framework]["components"]:
                framework_data[component] = f"Analysis of {component} for {trend_name} in the {industry} industry."
            
            analysis["assessment"][framework] = framework_data
    
    return analysis

def generate_strategy_document(analysis: Dict[str, Any], format: str = "html") -> Dict[str, Any]:
    """
    Generate a comprehensive strategy document based on the analysis
    
    Args:
        analysis: Analysis results to include in the document
        format: Output format (html or pdf)
        
    Returns:
        Dictionary with the generated document
    """
    logger.info(f"Generating strategy document for trend: {analysis.get('trend_name', '')}")
    
    if format == "html":
        document = generate_html_document(analysis)
    else:
        document = generate_html_document(analysis)  # Default to HTML for now
    
    return {
        "document": document,
        "format": format
    }

def generate_html_document(analysis: Dict[str, Any]) -> str:
    """
    Generate an HTML strategy document
    
    Args:
        analysis: Analysis results
        
    Returns:
        HTML document string
    """
    trend_name = analysis.get("trend_name", "Sustainability Trend")
    industry = analysis.get("industry", "General")
    timeframe = analysis.get("timeframe", "Medium term")
    summary = analysis.get("summary", "")
    recommendations = analysis.get("recommendations", [])
    strategic_actions = analysis.get("strategic_actions", [])
    opportunities = analysis.get("opportunities", [])
    threats = analysis.get("threats", [])
    assessment = analysis.get("assessment", {})
    
    # Current date for the document
    current_date = datetime.now().strftime("%B %d, %Y")
    
    # Generate HTML document
    html = f"""
    <div class="strategy-document">
        <div class="document-header text-center mb-5">
            <h1 class="mb-3">Strategic Analysis Report</h1>
            <h2>{trend_name}</h2>
            <p class="text-muted">Industry: {industry} | Timeframe: {timeframe} | Date: {current_date}</p>
        </div>
        
        <div class="document-section mb-5">
            <h3 class="section-title">Executive Summary</h3>
            <div class="card">
                <div class="card-body">
                    <p>{summary}</p>
                </div>
            </div>
        </div>
        
        <div class="document-section mb-5">
            <h3 class="section-title">Strategic Recommendations</h3>
            <div class="card">
                <div class="card-body">
                    <ol class="recommendation-list">
    """
    
    for recommendation in recommendations:
        html += f"                        <li>{recommendation}</li>\n"
    
    html += """
                    </ol>
                </div>
            </div>
        </div>
        
        <div class="document-section mb-5">
            <h3 class="section-title">Implementation Plan</h3>
            <div class="card">
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-6">
                            <h4>Strategic Actions</h4>
                            <ol class="implementation-list">
    """
    
    for action in strategic_actions:
        html += f"                                <li>{action}</li>\n"
    
    html += """
                            </ol>
                        </div>
                        <div class="col-md-6">
                            <h4>Key Performance Indicators</h4>
                            <ul class="kpi-list">
                                <li>Implementation progress against timeline</li>
                                <li>Resource utilization efficiency</li>
                                <li>Stakeholder engagement metrics</li>
                                <li>Business impact measurements</li>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="document-section mb-5">
            <h3 class="section-title">Opportunity & Risk Analysis</h3>
            <div class="card">
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-6">
                            <h4 class="text-success"><i class="fas fa-arrow-up me-2"></i>Opportunities</h4>
                            <ul class="opportunity-list">
    """
    
    for opportunity in opportunities:
        html += f"                                <li>{opportunity}</li>\n"
    
    html += """
                            </ul>
                        </div>
                        <div class="col-md-6">
                            <h4 class="text-danger"><i class="fas fa-arrow-down me-2"></i>Threats</h4>
                            <ul class="threat-list">
    """
    
    for threat in threats:
        html += f"                                <li>{threat}</li>\n"
    
    html += """
                            </ul>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="document-section mb-5">
            <h3 class="section-title">Framework Analysis</h3>
    """
    
    for framework_name, framework_data in assessment.items():
        html += f"""
            <div class="card mb-4">
                <div class="card-header">
                    <h4>{framework_name}</h4>
                </div>
                <div class="card-body">
        """
        
        if isinstance(framework_data, dict):
            for component, analysis_text in framework_data.items():
                html += f"""
                    <div class="mb-3">
                        <h5>{component}</h5>
                        <p>{analysis_text}</p>
                    </div>
                """
        else:
            html += f"<p>{framework_data}</p>"
        
        html += """
                </div>
            </div>
        """
    
    html += """
        </div>
        
        <div class="document-section mb-5">
            <h3 class="section-title">Next Steps</h3>
            <div class="card">
                <div class="card-body">
                    <p>Based on this strategic analysis, we recommend the following next steps:</p>
                    <ol>
                        <li>Review this analysis with key stakeholders to gather feedback</li>
                        <li>Prioritize recommendations based on business impact and feasibility</li>
                        <li>Develop a detailed implementation roadmap with timelines and responsibilities</li>
                        <li>Allocate resources and budget for implementation</li>
                        <li>Set up a governance structure to oversee implementation and track progress</li>
                    </ol>
                </div>
            </div>
        </div>
        
        <div class="document-footer text-center mt-5">
            <p class="text-muted">This report was generated by SustainaTrend™ AI Strategy Consultant</p>
            <p class="text-muted small">Confidential and proprietary information</p>
        </div>
    </div>
    """
    
    return html

# Flask routes
try:
    from flask import Blueprint, request, jsonify

    # Create a blueprint for the AI consultant
    ai_consultant_bp = Blueprint('ai_consultant', __name__)

    @ai_consultant_bp.route('/api/strategy/analyze-trend', methods=['POST'])
    def api_analyze_trend():
        """API endpoint for trend analysis"""
        try:
            data = request.json
            
            # Extract parameters
            trend_name = data.get('trend_name', '')
            industry = data.get('industry', 'General')
            timeframe = data.get('timeframe', 'medium')
            frameworks = data.get('frameworks', ["STEPPS", "Porter's Five Forces"])
            
            # Validate input
            if not trend_name:
                return jsonify({"error": "Trend name is required"}), 400
                
            # Analyze trend
            analysis = analyze_trend(trend_name, industry, timeframe, frameworks)
            
            # Integrate trend analytics from other modules
            analysis = integrate_trend_analytics(analysis, frameworks)
            
            return jsonify(analysis)
            
        except Exception as e:
            logger.error(f"Error in API endpoint: {e}")
            return jsonify({"error": str(e)}), 500

    @ai_consultant_bp.route('/api/strategy/generate-document', methods=['POST'])
    def api_generate_document():
        """API endpoint for document generation"""
        try:
            data = request.json
            
            # Extract parameters
            analysis = data.get('analysis', {})
            format = data.get('format', 'html')
            
            # Validate input
            if not analysis:
                return jsonify({"error": "Analysis data is required"}), 400
                
            # Generate document
            document = generate_strategy_document(analysis, format)
            
            return jsonify(document)
            
        except Exception as e:
            logger.error(f"Error in API endpoint: {e}")
            return jsonify({"error": str(e)}), 500

    def register_routes(app):
        """Register routes with Flask app"""
        app.register_blueprint(ai_consultant_bp)
        logger.info("AI Strategy Consultant routes registered successfully")

except ImportError:
    # Flask not available
    def register_routes(app):
        logger.warning("Flask not available, routes not registered")

# Example usage
if __name__ == "__main__":
    # Test the module
    analysis = analyze_trend("Carbon Footprint Transparency", "Technology", "medium", 
                           ["STEPPS", "Porter's Five Forces"])
    print(json.dumps(analysis, indent=2))