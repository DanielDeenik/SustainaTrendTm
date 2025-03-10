"""
Sustainability Co-Pilot Module for SustainaTrend™ Intelligence Platform

This module provides a powerful conversational AI assistant that helps
users navigate sustainability metrics, trends, and insights throughout the platform.

Key features:
1. Context-aware AI assistant that understands sustainability concepts
2. Natural language interface for complex sustainability queries
3. Seamless integration with Gemini API for high-quality responses
4. Knowledge-grounded responses with source attribution
5. Context-sensitive suggestions based on current page and user history
"""

import os
import time
import json
import logging
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

try:
    from flask import Blueprint, request, jsonify, current_app
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False
    logging.warning("Flask not available, some Co-Pilot functionality will be limited")

# Setup module logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Import Gemini search controller if available
try:
    from gemini_search import GeminiSearchController
    gemini_search_controller = GeminiSearchController()
    GEMINI_AVAILABLE = True
    logger.info("Sustainability Co-Pilot initialized with Gemini AI")
except ImportError:
    GEMINI_AVAILABLE = False
    gemini_search_controller = None
    logger.warning("Gemini API not available, Co-Pilot will use fallback mode")

# Blueprint for Flask routes
copilot_blueprint = Blueprint('sustainability_copilot', __name__)

# In-memory storage for conversation history (in production would use a database)
CONVERSATIONS = {}

# Default suggested prompts by context
DEFAULT_PROMPTS = {
    "general": [
        "What are the latest sustainability trends?",
        "Explain ESG reporting requirements",
        "How can I improve my carbon metrics?",
        "What is the ESRS framework?",
        "Show me sustainability performance by industry"
    ],
    "dashboard": [
        "Explain this carbon emissions trend",
        "Compare our metrics to industry benchmarks",
        "What actions would improve our ESG score?",
        "Generate a report summary of these metrics",
        "What's causing this spike in energy usage?"
    ],
    "trend-analysis": [
        "Predict sustainability trends for next quarter",
        "Which metrics are most volatile?",
        "How do these trends compare to competitors?",
        "What factors are driving these trends?",
        "Create a narrative explaining these trend patterns"
    ],
    "document-upload": [
        "Extract key sustainability metrics from this report",
        "Compare this report to ESRS requirements",
        "What's missing in this sustainability disclosure?",
        "Summarize the climate targets in this document",
        "Find all carbon reduction commitments"
    ]
}

class SustainabilityCopilot:
    """Main class for the Sustainability Co-Pilot functionality"""
    
    def __init__(self):
        """Initialize the Sustainability Co-Pilot"""
        self.available = GEMINI_AVAILABLE
        self.gemini_controller = gemini_search_controller if GEMINI_AVAILABLE else None
        logger.info(f"Sustainability Co-Pilot is {'available' if self.available else 'not available'}")
    
    def get_suggested_prompts(self, context: str = "general", page: str = "", 
                              conversation_id: Optional[str] = None) -> List[str]:
        """
        Get context-aware suggested prompts for the Co-Pilot
        
        Args:
            context: Context category for the prompts (general, dashboard, etc.)
            page: Current page in the platform
            conversation_id: Optional ID of the current conversation for continuity
            
        Returns:
            List of suggested prompts
        """
        # Start with default prompts based on context
        if context in DEFAULT_PROMPTS:
            prompts = DEFAULT_PROMPTS[context].copy()
        else:
            prompts = DEFAULT_PROMPTS["general"].copy()
            
        # Adjust prompts based on current page if not already using a page-specific context
        if context == "general" and page:
            page_clean = page.replace('-', '').replace('_', '').lower()
            
            if "dashboard" in page_clean:
                prompts[0] = "Explain these dashboard metrics"
                prompts[1] = "What actions would improve our numbers?"
            elif "trend" in page_clean:
                prompts[0] = "Analyze these sustainability trends"
                prompts[1] = "What's driving this trend pattern?"
            elif "document" in page_clean or "upload" in page_clean:
                prompts[0] = "Analyze my sustainability report"
                prompts[1] = "Check my report against ESRS requirements"
            elif "search" in page_clean:
                prompts[0] = "Find sustainability metrics for renewable energy"
                prompts[1] = "How do these search results relate to our goals?"
            elif "story" in page_clean or "storytelling" in page_clean:
                prompts[0] = "Generate a sustainability narrative"
                prompts[1] = "Create a story from our metrics data"
                
        # Add personalized prompts based on conversation history if available
        if conversation_id and conversation_id in CONVERSATIONS:
            history = CONVERSATIONS[conversation_id]
            if len(history) > 1:
                # Extract concepts from previous conversation to create follow-up prompts
                recent_topics = self._extract_topics_from_history(history[-3:] if len(history) >= 3 else history)
                if recent_topics:
                    follow_up_prompt = f"Tell me more about {recent_topics[0]}"
                    comparison_prompt = f"How does {recent_topics[0]} compare to industry standards?"
                    prompts = [follow_up_prompt, comparison_prompt] + prompts[:3]
        
        return prompts
    
    def process_query(self, query: str, context: str = "general", 
                     page: str = "", conversation_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Process a user query and generate a response
        
        Args:
            query: The user's natural language query
            context: Context category for the query (general, dashboard, etc.)
            page: Current page in the platform
            conversation_id: Optional ID of the current conversation
            
        Returns:
            Response data including text, actions, facts, and conversation ID
        """
        # Create a new conversation ID if none provided
        if not conversation_id:
            conversation_id = f"conv-{uuid.uuid4()}"
            CONVERSATIONS[conversation_id] = []
        elif conversation_id not in CONVERSATIONS:
            CONVERSATIONS[conversation_id] = []
            
        # Add user query to conversation history
        CONVERSATIONS[conversation_id].append({
            "role": "user",
            "content": query,
            "timestamp": datetime.now().isoformat()
        })
        
        # Process based on available capabilities
        if self.available and self.gemini_controller:
            # Use Gemini for high-quality response generation
            response_data = self._generate_with_gemini(query, context, page, CONVERSATIONS[conversation_id])
        else:
            # Use fallback response generation
            response_data = self._generate_fallback_response(query, context, page, CONVERSATIONS[conversation_id])
            
        # Add response to conversation history
        CONVERSATIONS[conversation_id].append({
            "role": "assistant",
            "content": response_data["response"],
            "timestamp": datetime.now().isoformat(),
            "actions": response_data.get("actions", []),
            "facts": response_data.get("facts", [])
        })
        
        # Trim conversation history if it's getting too long
        if len(CONVERSATIONS[conversation_id]) > 20:
            CONVERSATIONS[conversation_id] = CONVERSATIONS[conversation_id][-20:]
            
        # Include conversation ID in response
        response_data["conversation_id"] = conversation_id
        
        return response_data
    
    def _generate_with_gemini(self, query: str, context: str, 
                             page: str, history: List[Dict]) -> Dict[str, Any]:
        """
        Generate a response using Gemini
        
        Args:
            query: User query
            context: Query context
            page: Current page
            history: Conversation history
            
        Returns:
            Response data
        """
        try:
            # Build prompt with conversation history, context, and query
            prompt = self._build_gemini_prompt(query, context, page, history)
            
            # Get response from Gemini
            model_name = self.gemini_controller._best_model or "gemini-pro"
            model = self.gemini_controller.genai.GenerativeModel(model_name=model_name)
            
            # Generate content
            response = model.generate_content(prompt)
            
            # Parse structured response (handle expected JSON format)
            if hasattr(response, 'text'):
                try:
                    # Try to parse as JSON if it's in the expected format
                    response_text = response.text.strip()
                    if response_text.startswith('{') and response_text.endswith('}'):
                        structured_response = json.loads(response_text)
                        return {
                            "response": structured_response.get("response", "I couldn't provide a proper response."),
                            "actions": structured_response.get("actions", []),
                            "facts": structured_response.get("facts", []),
                            "sources": structured_response.get("sources", [])
                        }
                    else:
                        # Not JSON, use as plain text response
                        return {
                            "response": response_text,
                            "actions": [],
                            "facts": []
                        }
                except json.JSONDecodeError:
                    # Fallback for non-JSON responses
                    return {
                        "response": response.text,
                        "actions": [],
                        "facts": []
                    }
            else:
                # Handle unexpected response format
                return {
                    "response": "I'm having trouble processing your request. Please try again.",
                    "actions": [],
                    "facts": []
                }
                
        except Exception as e:
            logger.error(f"Error generating response with Gemini: {str(e)}")
            return {
                "response": "I'm sorry, I encountered an error while processing your request. Please try again later.",
                "actions": [],
                "facts": []
            }
    
    def _build_gemini_prompt(self, query: str, context: str, page: str, history: List[Dict]) -> str:
        """
        Build a prompt for Gemini that includes context and conversation history
        
        Args:
            query: User query
            context: Query context
            page: Current page
            history: Conversation history
            
        Returns:
            Formatted prompt string
        """
        # Build system prompt with context
        if context == "dashboard":
            system_prompt = "You are the Sustainability Co-Pilot, an assistant that helps analyze sustainability metrics and performance data. Provide actionable insights based on the metrics being viewed."
        elif context == "trend-analysis":
            system_prompt = "You are the Sustainability Co-Pilot, an assistant that helps identify and explain sustainability trends. Provide context for what's driving these trends and make predictions."
        elif context == "document-upload":
            system_prompt = "You are the Sustainability Co-Pilot, an assistant that helps analyze sustainability reports and documents. Identify key metrics, compliance gaps, and improvement opportunities."
        else:
            system_prompt = "You are the Sustainability Co-Pilot, an assistant that provides sustainability intelligence insights. You're an expert in ESG frameworks, reporting standards, and sustainability metrics."
            
        # Add page-specific context if available
        if page:
            if page == "dashboard" or "dashboard" in page:
                system_prompt += " The user is viewing a dashboard with sustainability metrics including carbon emissions, energy usage, water consumption, and waste management data."
            elif page == "trend-analysis" or "trend" in page:
                system_prompt += " The user is viewing trend analysis for sustainability metrics, including historical data and projections."
            elif page == "document-upload" or "document" in page:
                system_prompt += " The user is working with a sustainability report document, looking to extract insights and compliance information."
        
        # Add response format instructions
        system_prompt += "\n\nProvide responses that include:\n"
        system_prompt += "1. A clear, concise answer to the user's question\n"
        system_prompt += "2. Relevant facts or data points when applicable\n"
        system_prompt += "3. Suggested actions the user might take\n"
        system_prompt += "4. Sources for your information when possible\n\n"
        system_prompt += "Format your response as a JSON object with the following structure:\n"
        system_prompt += "{\n  \"response\": \"Your main response text\",\n  \"facts\": [\"Fact 1\", \"Fact 2\"],\n  \"actions\": [{\"label\": \"Action button text\", \"action\": \"URL or action identifier\"}],\n  \"sources\": [\"Source 1\", \"Source 2\"]\n}\n\n"
        
        # Add conversation history (limited to last 5 exchanges)
        history_prompt = ""
        if history and len(history) > 0:
            recent_history = history[-10:] if len(history) > 10 else history
            history_prompt = "Previous conversation:\n"
            for msg in recent_history:
                role = "User" if msg["role"] == "user" else "Assistant"
                history_prompt += f"{role}: {msg['content']}\n"
            history_prompt += "\n"
        
        # Combine all parts into final prompt
        final_prompt = f"{system_prompt}\n{history_prompt}User: {query}\nAssistant:"
        
        return final_prompt
        
    def _generate_fallback_response(self, query: str, context: str, 
                                  page: str, history: List[Dict]) -> Dict[str, Any]:
        """
        Generate a fallback response when Gemini is not available
        
        Args:
            query: User query
            context: Query context
            page: Current page
            history: Conversation history
            
        Returns:
            Response data
        """
        # Define some fallback responses based on recognized keywords
        query_lower = query.lower()
        
        # Check for metrics-related queries
        if any(word in query_lower for word in ["metrics", "kpi", "data", "carbon", "emissions", "measure"]):
            return {
                "response": "I understand you're asking about sustainability metrics. While I'm operating in fallback mode with limited capabilities, I can tell you that comprehensive sustainability metrics typically include carbon emissions (Scope 1, 2, and 3), energy usage, water consumption, waste management, and social impact indicators. For more specific analysis, please try again when our Gemini AI connection is restored.",
                "facts": [
                    "Carbon metrics typically include Scope 1 (direct), Scope 2 (purchased energy), and Scope 3 (value chain) emissions",
                    "The GHG Protocol is the most widely used accounting framework for greenhouse gas emissions",
                    "ESG metrics span environmental, social, and governance dimensions of sustainability"
                ],
                "actions": [
                    {"label": "View Dashboard", "action": "/dashboard"},
                    {"label": "Learn About ESRS", "action": "/esrs-framework"}
                ]
            }
        
        # Check for trend-related queries
        elif any(word in query_lower for word in ["trend", "prediction", "forecast", "future", "analysis"]):
            return {
                "response": "You're asking about sustainability trends or predictions. In fallback mode, I can share that current global trends include increased focus on climate disclosure regulations, transition to renewable energy, circular economy adoption, and greater emphasis on biodiversity impact. For deeper analysis of specific trends, please try again when our AI services are fully operational.",
                "facts": [
                    "The EU's Corporate Sustainability Reporting Directive (CSRD) represents a significant regulatory trend",
                    "Science-based targets are becoming standard practice for climate commitments",
                    "Investors increasingly use ESG performance for investment decisions"
                ],
                "actions": [
                    {"label": "View Trend Analysis", "action": "/trend-analysis"},
                    {"label": "Check Industry Benchmarks", "action": "/sustainability"}
                ]
            }
            
        # Check for report or document-related queries
        elif any(word in query_lower for word in ["report", "document", "disclosure", "framework", "standard", "esrs"]):
            return {
                "response": "I see you're asking about sustainability reporting frameworks or standards. Even in fallback mode, I can tell you that key frameworks include the European Sustainability Reporting Standards (ESRS), Global Reporting Initiative (GRI), Sustainability Accounting Standards Board (SASB), and Task Force on Climate-related Financial Disclosures (TCFD). These frameworks provide standardized approaches to sustainability disclosure.",
                "facts": [
                    "ESRS is mandatory for many EU companies under the CSRD directive",
                    "GRI is the most widely used global standard for sustainability reporting",
                    "SASB focuses on financially material sustainability topics"
                ],
                "actions": [
                    {"label": "Analyze Documents", "action": "/document-upload"},
                    {"label": "ESRS Framework Details", "action": "/esrs-framework"}
                ]
            }
            
        # Generic fallback for other queries
        else:
            return {
                "response": "I'm currently operating in fallback mode with limited capabilities. I understand you're asking about sustainability topics, but I need my full AI capabilities to give you a more specific and helpful response. Please try your query again when our Gemini AI connection is restored. In the meantime, you can explore our dashboard or trend analysis sections for sustainability insights.",
                "facts": [
                    "The SustainaTrend platform offers metrics dashboards, trend analysis, and document analysis",
                    "You can upload sustainability reports for automated analysis",
                    "Real-time sustainability data is available in the dashboard"
                ],
                "actions": [
                    {"label": "View Dashboard", "action": "/dashboard"},
                    {"label": "Explore Trends", "action": "/trend-analysis"}
                ]
            }
    
    def _extract_topics_from_history(self, recent_history: List[Dict]) -> List[str]:
        """
        Extract key topics from conversation history for personalized suggestions
        
        Args:
            recent_history: Recent conversation history entries
            
        Returns:
            List of identified topics
        """
        topics = []
        
        # Extract topics from user queries and responses
        for entry in recent_history:
            content = entry["content"].lower()
            
            # Check for sustainability topics
            if "carbon" in content or "emission" in content:
                topics.append("carbon emissions")
            if "energy" in content:
                topics.append("energy efficiency")
            if "water" in content:
                topics.append("water usage")
            if "waste" in content:
                topics.append("waste management")
            if "social" in content:
                topics.append("social metrics")
            if "governance" in content:
                topics.append("governance")
            if "biodiversity" in content:
                topics.append("biodiversity impact")
            if "esrs" in content or "csrd" in content:
                topics.append("ESRS compliance")
            if "report" in content or "reporting" in content:
                topics.append("sustainability reporting")
            if "trend" in content or "forecast" in content:
                topics.append("sustainability trends")
                
        # Remove duplicates and return
        return list(set(topics))

# Initialize Co-Pilot
copilot = SustainabilityCopilot()

# Blueprint routes - only create if Flask is available
if FLASK_AVAILABLE:
    @copilot_blueprint.route('/api/sustainability-copilot/query', methods=['POST'])
    def copilot_query():
        """API endpoint for Co-Pilot queries"""
        try:
            data = request.json
            query = data.get('query', '')
            context = data.get('context', 'general')
            page = data.get('page', '')
            conversation_id = data.get('conversation_id')
            
            if not query:
                return jsonify({"error": "No query provided"}), 400
                
            logger.info(f"Co-Pilot query received: '{query}' (context: {context}, page: {page})")
            
            response_data = copilot.process_query(query, context, page, conversation_id)
            
            logger.info(f"Co-Pilot response generated for query: '{query}'")
            return jsonify(response_data)
            
        except Exception as e:
            logger.error(f"Error processing Co-Pilot query: {str(e)}")
            return jsonify({
                "error": "Failed to process query",
                "response": "I'm sorry, I encountered an error while processing your request. Please try again later.",
                "actions": [],
                "facts": []
            }), 500
            
    @copilot_blueprint.route('/api/sustainability-copilot/suggested-prompts', methods=['GET'])
    def copilot_suggested_prompts():
        """API endpoint for Co-Pilot suggested prompts"""
        try:
            context = request.args.get('context', 'general')
            page = request.args.get('page', '')
            conversation_id = request.args.get('conversation_id')
            
            logger.info(f"Co-Pilot suggested prompts requested (context: {context}, page: {page})")
            
            prompts = copilot.get_suggested_prompts(context, page, conversation_id)
            
            return jsonify({"prompts": prompts})
            
        except Exception as e:
            logger.error(f"Error getting Co-Pilot suggested prompts: {str(e)}")
            return jsonify({"error": "Failed to get suggested prompts", "prompts": []}), 500

def register_routes(app):
    """
    Register the Sustainability Co-Pilot routes with a Flask application
    
    Args:
        app: Flask application
    """
    if FLASK_AVAILABLE:
        app.register_blueprint(copilot_blueprint)
        logger.info("Sustainability Co-Pilot routes registered successfully")
    else:
        logger.error("Cannot register Sustainability Co-Pilot routes: Flask not available")