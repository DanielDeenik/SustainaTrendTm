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
        Get context-aware suggested prompts for the Co-Pilot using structured templates
        
        Args:
            context: Context category for the prompts (general, dashboard, etc.)
            page: Current page in the platform
            conversation_id: Optional ID of the current conversation for continuity
            
        Returns:
            List of suggested prompts
        """
        # Map context to template contexts (similar to prompt building function)
        # Clean up context string for template matching
        template_context = context.lower().replace('-', '_').replace(' ', '_')
        
        # Standard context mapping
        context_map = {
            "dashboard": "dashboard",
            "real_estate": "real_estate",
            "realestate": "real_estate",
            "trend_analysis": "trend_analysis",
            "trend-analysis": "trend_analysis",
            "document_analysis": "document_analysis", 
            "document_upload": "document_analysis",
            "document-upload": "document_analysis",
            "stories": "stories",
            "sustainability_stories": "stories",
            "search": "search",
            "esrs": "esrs",
            "esrs_framework": "esrs"
        }
        
        # Get the mapped context or use general as fallback
        template_context = context_map.get(template_context, "general")
        
        # Context-specific prompts based on structured templates
        context_prompts = {
            "dashboard": [
                "Explain these sustainability metrics",
                "Which metrics need improvement?",
                "Benchmark these metrics against industry standards",
                "What actions will improve our sustainability score?",
                "Show trends in our carbon emissions"
            ],
            "real_estate": [
                "How to improve building efficiency?",
                "Compare my properties to industry benchmarks",
                "What retrofits give the best ROI?",
                "How does this property's EPC rating compare to market?",
                "What green certifications should we pursue?"
            ],
            "trend_analysis": [
                "What do these sustainability trends indicate?",
                "Predict future sustainability trends",
                "How do these trends compare to market averages?",
                "Which emerging sustainability topics should we monitor?",
                "What competitive intelligence can we derive from these trends?"
            ],
            "document_analysis": [
                "Analyze this sustainability report",
                "Identify compliance gaps in this document",
                "Extract key metrics from this report",
                "How does this report compare to best practices?",
                "What areas of this report need improvement?"
            ],
            "stories": [
                "Generate a sustainability narrative from our data",
                "Create a compelling story from these metrics",
                "How can we better communicate our sustainability progress?",
                "What storytelling approach works best for our data?",
                "How should we frame our environmental impact story?"
            ],
            "search": [
                "Find information about carbon accounting",
                "What are the latest sustainability reporting standards?",
                "Search for green building certifications",
                "Find best practices for ESG disclosure",
                "What companies are leading in sustainability?"
            ],
            "esrs": [
                "Explain ESRS compliance requirements",
                "What disclosures are required under ESRS E1?",
                "How does ESRS compare to other frameworks?",
                "What are the deadlines for ESRS reporting?",
                "How should we prepare for ESRS compliance?"
            ],
            "general": DEFAULT_PROMPTS["general"].copy()
        }
        
        # Get prompts for the current context or fall back to general
        prompts = context_prompts.get(template_context, context_prompts["general"])
        
        # If page context provides additional specificity, refine prompts
        if page and template_context == "general":
            page_clean = page.lower().replace('-', ' ').replace('_', ' ')
            
            # Specific page-level refinements
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
                     page: str = "", conversation_id: Optional[str] = None,
                     structured_prompt: Optional[str] = None) -> Dict[str, Any]:
        """
        Process a user query and generate a response
        
        Args:
            query: The user's natural language query
            context: Context category for the query (general, dashboard, etc.)
            page: Current page in the platform
            conversation_id: Optional ID of the current conversation
            structured_prompt: Optional structured prompt from client templates
            
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
            response_data = self._generate_with_gemini(
                query, 
                context, 
                page, 
                CONVERSATIONS[conversation_id],
                structured_prompt
            )
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
                             page: str, history: List[Dict],
                             structured_prompt: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate a response using Gemini
        
        Args:
            query: User query
            context: Query context
            page: Current page
            history: Conversation history
            structured_prompt: Optional structured prompt from client
            
        Returns:
            Response data
        """
        try:
            # Use client-provided structured prompt if available, otherwise build our own
            if structured_prompt:
                logger.info(f"Using client-provided structured prompt for context: {context}")
                prompt = f"{structured_prompt}\n\nUser: {query}\nAssistant:"
            else:
                # Build prompt with conversation history, context, and query
                prompt = self._build_gemini_prompt(query, context, page, history)
            
            # Get response from Gemini
            try:
                # Use the controller's best model if available, or fallback to gemini-pro
                model_name = "gemini-pro"
                if hasattr(self.gemini_controller, 'best_model'):
                    model_name = self.gemini_controller.best_model
                elif hasattr(self.gemini_controller, '_best_model'):
                    model_name = self.gemini_controller._best_model
                    
                # Create model
                model = None
                if hasattr(self.gemini_controller, 'genai'):
                    # Try to get available models
                    available_models = []
                    try:
                        available_models = list(self.gemini_controller.genai.list_models())
                        model_names = [m.name for m in available_models]
                        logger.info(f"Available Gemini models: {model_names}")
                        
                        # Use first available model if our preferred one isn't available
                        if available_models and model_name not in model_names:
                            model_name = available_models[0].name
                            logger.info(f"Using alternative model: {model_name}")
                    except Exception as e:
                        logger.warning(f"Could not list available models: {str(e)}")
                    
                    # Create the model with best available name
                    model = self.gemini_controller.genai.GenerativeModel(model_name=model_name)
                else:
                    raise ValueError("Gemini API not properly initialized")
                
                # Generate content
                response = model.generate_content(prompt)
                
            except Exception as model_error:
                logger.error(f"Error using Gemini model: {str(model_error)}")
                return self._generate_fallback_response(query, context, page, history)
            
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
        Build a structured prompt for Gemini that includes context and conversation history
        Uses predefined prompt templates for different contexts
        
        Args:
            query: User query
            context: Query context
            page: Current page
            history: Conversation history
            
        Returns:
            Formatted prompt string
        """
        # Map context to template contexts
        # Clean up context string for template matching
        template_context = context.lower().replace('-', '_').replace(' ', '_')
        
        # Standard context mapping
        context_map = {
            "dashboard": "dashboard",
            "real_estate": "real_estate",
            "trend_analysis": "trend_analysis",
            "document_analysis": "document_analysis", 
            "document_upload": "document_analysis",
            "stories": "stories",
            "sustainability_stories": "stories",
            "search": "search",
            "esrs": "esrs",
            "esrs_framework": "esrs"
        }
        
        # Get the mapped context or use general as fallback
        template_context = context_map.get(template_context, "general")
        
        # Build system prompt with template structure
        if template_context == "dashboard":
            system_prompt = """You are the Sustainability Co-Pilot for SustainaTrend™, an expert AI assistant specializing in sustainability intelligence.
You're currently helping with the main dashboard which shows portfolio-wide sustainability metrics.
Format your responses to be concise and action-oriented, focusing on insights rather than descriptions.
Include specific metrics when available and suggest concrete next steps."""
        elif template_context == "real_estate":
            system_prompt = """You are the Sustainability Co-Pilot for SustainaTrend™, an expert AI assistant specializing in real estate sustainability.
You're currently helping with the real estate portfolio view which shows property-specific environmental performance.
Focus on practical building improvements, energy efficiency, certification paths, and financial benefits of sustainable practices.
Provide specific, actionable recommendations relevant to property types in the portfolio."""
        elif template_context == "trend_analysis":
            system_prompt = """You are the Sustainability Co-Pilot for SustainaTrend™, an expert AI assistant specializing in sustainability trend analysis.
You're currently helping with the trend analysis view which tracks emerging sustainability themes and market trends.
Focus on identifying patterns, predicting future developments, and connecting trends to strategic opportunities.
Highlight emerging risks, market sentiment shifts, and competitive intelligence."""
        elif template_context == "document_analysis":
            system_prompt = """You are the Sustainability Co-Pilot for SustainaTrend™, an expert AI assistant specializing in sustainability document analysis.
You're currently helping with the document analysis view which examines sustainability reports and ESG disclosures.
Focus on extracting key metrics, evaluating compliance with reporting frameworks, and identifying gaps or opportunities.
Provide insights on report quality, completeness, and comparability to industry standards."""
        elif template_context == "stories":
            system_prompt = """You are the Sustainability Co-Pilot for SustainaTrend™, an expert AI assistant specializing in sustainability storytelling.
You're currently helping with the sustainability stories view which transforms data into compelling narratives.
Focus on creating impactful, accurate, and engaging stories that effectively communicate sustainability progress.
Suggest narrative structures, key message points, and suitable data visualizations."""
        elif template_context == "search":
            system_prompt = """You are the Sustainability Co-Pilot for SustainaTrend™, an expert AI assistant specializing in sustainability information retrieval.
You're currently helping with the search view which helps users find relevant sustainability information and resources.
Focus on understanding search intent, suggesting relevant filters, and providing context for search results.
Help users refine their searches and connect them to the most valuable resources."""
        elif template_context == "esrs":
            system_prompt = """You are the Sustainability Co-Pilot for SustainaTrend™, an expert AI assistant specializing in ESRS compliance.
You're currently helping with the ESRS framework view which guides organizations on compliance with European Sustainability Reporting Standards.
Focus on practical implementation guidance, disclosure requirements, and compliance strategies.
Provide specific, actionable insights tailored to the organization's context and reporting maturity."""
        else:
            system_prompt = """You are the Sustainability Co-Pilot for SustainaTrend™, an expert AI assistant specializing in sustainability intelligence.
You provide knowledgeable, practical guidance on sustainability topics across environmental, social, and governance domains.
Keep responses concise, factual, and practical with a focus on actionable insights.
When appropriate, suggest relevant areas of the platform to explore for more detailed information."""
            
        # Add page-specific context if available
        if page:
            page_clean = page.lower().replace('-', ' ').replace('_', ' ')
            
            if "dashboard" in page_clean:
                system_prompt += "\n\nThe user is viewing a dashboard with sustainability metrics including carbon emissions, energy usage, water consumption, and waste management data."
            elif "trend" in page_clean and "analysis" in page_clean:
                system_prompt += "\n\nThe user is viewing trend analysis for sustainability metrics, including historical data and projections."
            elif "document" in page_clean or "upload" in page_clean:
                system_prompt += "\n\nThe user is working with a sustainability report document, looking to extract insights and compliance information."
            elif "realestate" in page_clean or "real estate" in page_clean:
                system_prompt += "\n\nThe user is viewing real estate property sustainability data, including energy ratings, carbon footprint, and retrofit opportunities."
            elif "stories" in page_clean or "storytelling" in page_clean:
                system_prompt += "\n\nThe user is working with sustainability storytelling tools to create compelling narratives from sustainability data."
            elif "search" in page_clean:
                system_prompt += "\n\nThe user is searching for sustainability information and resources."
            elif "esrs" in page_clean:
                system_prompt += "\n\nThe user is working with ESRS compliance tools to prepare for European Sustainability Reporting Standards requirements."
        
        # Add response format instructions
        system_prompt += "\n\nProvide responses that include:\n"
        system_prompt += "1. A clear, concise answer to the user's question\n"
        system_prompt += "2. Relevant facts or data points when applicable\n"
        system_prompt += "3. Suggested actions the user might take\n"
        system_prompt += "4. Sources for your information when possible\n\n"
        system_prompt += "Format your response as a JSON object with the following structure:\n"
        system_prompt += "{\n  \"response\": \"Your main response text\",\n  \"facts\": [\"Fact 1\", \"Fact 2\"],\n  \"actions\": [{\"label\": \"Action button text\", \"action\": \"URL or action identifier\"}],\n  \"sources\": [\"Source 1\", \"Source 2\"]\n}\n\n"
        
        # Add conversation history (limited to last 10 exchanges for context)
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
        
        # Check for context-specific queries
        if context == "real_estate" and any(word in query_lower for word in ["property", "building", "retrofit", "epc", "energy", "efficiency", "certification", "roi"]):
            return {
                "response": "I understand you're asking about real estate sustainability improvements. In fallback mode, I can tell you that the retrofits with best ROI typically include LED lighting (1-3 years payback), energy management systems (2-4 years), HVAC optimization (3-5 years), and building envelope improvements (5-10 years). For specific ROI calculations based on your property portfolio, please try again when our AI services are fully operational.",
                "facts": [
                    "Energy efficiency retrofits typically show ROI between 10-25% depending on property type and location",
                    "Building certification programs like BREEAM, LEED, and WELL can increase property value by 3-7%",
                    "The EU's Energy Performance of Buildings Directive requires all new buildings to be nearly zero-energy by 2030"
                ],
                "actions": [
                    {"label": "View Real Estate Dashboard", "action": "/realestate-trends"},
                    {"label": "Energy Efficiency Calculator", "action": "/sustainability"}
                ]
            }
        
        # Check for metrics-related queries
        elif any(word in query_lower for word in ["metrics", "kpi", "data", "carbon", "emissions", "measure"]):
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
            structured_prompt = data.get('structured_prompt')
            
            if not query:
                return jsonify({"error": "No query provided"}), 400
                
            logger.info(f"Co-Pilot query received: '{query}' (context: {context}, page: {page})")
            
            # Log if a structured prompt was received from the client
            if structured_prompt:
                logger.info(f"Received structured prompt from client for context: {context}")
            
            # Pass structured prompt to the process_query method
            response_data = copilot.process_query(
                query, 
                context, 
                page, 
                conversation_id, 
                structured_prompt=structured_prompt
            )
            
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