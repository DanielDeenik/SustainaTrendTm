"""
Regulatory AI Agent Module for SustainaTrend™ (Refactored)

This module provides AI-powered regulatory compliance assessment and analysis
for sustainability reports and ESG disclosures.

Key features:
1. Regulatory framework assessment across multiple jurisdictions
2. AI-powered compliance gap analysis
3. Timeline recommendations for regulatory transitions
4. Visual compliance reporting dashboard

This is the refactored version that uses the shared regulatory AI service.
"""

import json
import logging
import os
import sys
import uuid
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

# Flask imports
try:
    from flask import Blueprint, render_template, request, jsonify, current_app, send_from_directory
except ImportError:
    # Fallback for Flask import
    backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    if backend_path not in sys.path:
        sys.path.append(backend_path)
    try:
        from flask import Blueprint, render_template, request, jsonify, current_app, send_from_directory
    except ImportError as e:
        print(f"Error importing Flask: {e}")
        # Define stub classes for type checking only
        class Blueprint:
            def __init__(self, *args, **kwargs): pass
            def route(self, *args, **kwargs): 
                def decorator(f): return f
                return decorator
        class Request:
            args = {}
            json = {}
            files = {}
            form = {}
        request = Request()
        
        def render_template(*args, **kwargs): pass
        def jsonify(*args, **kwargs): pass

# Set up logging
logger = logging.getLogger(__name__)

# Import shared regulatory AI service
try:
    from frontend.services.regulatory_ai_service import (
        get_supported_frameworks,
        analyze_document_compliance,
        generate_compliance_visualization_data,
        handle_document_upload,
        get_upload_folder
    )
    from frontend.services.ai_connector import (
        connect_to_ai_services,
        is_pinecone_available
    )
    # Initialize AI connector
    connect_to_ai_services()
    logger.info("AI connector module loaded successfully")
    # Log Pinecone availability
    pinecone_status = "Connected" if is_pinecone_available() else "Not connected"
    logger.info(f"Pinecone RAG system availability: {pinecone_status}")
    logger.info("Imported refactored regulatory_ai_agent via regular import")
except ImportError as e:
    logger.warning(f"Error importing regulatory AI service: {str(e)}")
    # Create stub functions for development
    def get_supported_frameworks(): return {"CSRD": "Corporate Sustainability Reporting Directive"}
    def analyze_document_compliance(text, frameworks=None): return {"frameworks": {}}
    def generate_compliance_visualization_data(results): return {"frameworks": []}
    def handle_document_upload(file): return (False, "Service unavailable", None)
    def get_upload_folder(): return os.path.join(os.path.dirname(__file__), 'uploads')
logger = logging.getLogger(__name__)

# Create blueprint with a different name to avoid conflicts
regulatory_ai_bp = Blueprint('regulatory_ai_refactored', __name__, url_prefix='/regulatory-ai-refactored')

# AI connector imports
try:
    from frontend.utils.ai_connector import get_generative_ai, generate_embedding, get_rag_system, is_pinecone_available
    AI_CONNECTOR_AVAILABLE = True
    RAG_AVAILABLE = is_pinecone_available()
    logger.info("AI connector module loaded successfully")
    logger.info(f"Pinecone RAG system availability: {'Connected' if RAG_AVAILABLE else 'Using fallback'}")
except ImportError:
    try:
        # Fallback to relative import
        from utils.ai_connector import get_generative_ai, generate_embedding, get_rag_system, is_pinecone_available
        AI_CONNECTOR_AVAILABLE = True
        RAG_AVAILABLE = is_pinecone_available()
        logger.info("AI connector module loaded successfully from relative path")
    except ImportError as e:
        AI_CONNECTOR_AVAILABLE = False
        RAG_AVAILABLE = False
        logger.warning(f"AI connector not available, using fallback regulatory assessment: {str(e)}")

# Regulatory framework data
REGULATORY_FRAMEWORKS = {
    "ESRS": {
        "full_name": "European Sustainability Reporting Standards",
        "description": "European standards for corporate sustainability reporting",
        "categories": {
            "E1": "Climate change mitigation",
            "E2": "Climate change adaptation",
            "E3": "Water and marine resources",
            "E4": "Biodiversity and ecosystems",
            "E5": "Resource use and circular economy",
            "S1": "Own workforce",
            "S2": "Workers in the value chain",
            "S3": "Affected communities",
            "S4": "Consumers and end-users",
            "G1": "Business conduct",
            "G2": "Governance, risk management and internal control"
        },
        "effective_date": "2024-01-01",
        "region": "European Union"
    },
    "CSRD": {
        "full_name": "Corporate Sustainability Reporting Directive",
        "description": "EU directive mandating sustainability reporting",
        "categories": {
            "P1": "General principles",
            "P2": "Business model and strategy",
            "P3": "Policies and due diligence",
            "P4": "Targets",
            "P5": "Role of administrative bodies"
        },
        "effective_date": "2023-01-01",
        "region": "European Union"
    },
    "SFDR": {
        "full_name": "Sustainable Finance Disclosure Regulation",
        "description": "EU regulation on sustainability-related disclosures",
        "categories": {
            "A1": "Integration of sustainability risks",
            "A2": "Principal adverse impacts",
            "A3": "Remuneration policies",
            "B1": "Sustainability risk policy",
            "B2": "Due diligence statement",
            "C1": "Product-level disclosures",
            "C2": "Entity-level disclosures"
        },
        "effective_date": "2021-03-10",
        "region": "European Union"
    },
    "TCFD": {
        "full_name": "Task Force on Climate-related Financial Disclosures",
        "description": "Framework for climate-related financial disclosures",
        "categories": {
            "G1": "Governance",
            "S1": "Strategy",
            "R1": "Risk Management",
            "M1": "Metrics and Targets"
        },
        "effective_date": "2017-06-29",
        "region": "Global"
    },
    "ISSB": {
        "full_name": "International Sustainability Standards Board",
        "description": "Global baseline for sustainability disclosures",
        "categories": {
            "S1": "General Requirements",
            "S2": "Climate-related Disclosures",
            "S3": "Biodiversity-related Disclosures",
            "S4": "Social-related Disclosures"
        },
        "effective_date": "2023-06-01",
        "region": "Global"
    }
}

# Timeline data for regulatory transitions
REGULATORY_TIMELINE = [
    {
        "date": "2023-01-01",
        "framework": "CSRD",
        "event": "First companies subject to CSRD reporting requirements (large companies already subject to NFRD)",
        "impact": "high"
    },
    {
        "date": "2024-01-01",
        "framework": "ESRS",
        "event": "First ESRS reporting period begins for companies already subject to NFRD",
        "impact": "high"
    },
    {
        "date": "2025-01-01",
        "framework": "CSRD",
        "event": "Large companies not previously subject to NFRD begin reporting",
        "impact": "medium"
    },
    {
        "date": "2026-01-01",
        "framework": "CSRD",
        "event": "Listed SMEs begin reporting (with opt-out until 2028)",
        "impact": "medium"
    },
    {
        "date": "2026-06-30",
        "framework": "ESRS",
        "event": "First ESRS reports due for companies already subject to NFRD",
        "impact": "high"
    },
    {
        "date": "2027-06-30",
        "framework": "ESRS",
        "event": "ESRS reports due for large companies not previously subject to NFRD",
        "impact": "medium"
    },
    {
        "date": "2028-06-30",
        "framework": "ESRS",
        "event": "ESRS reports due for listed SMEs",
        "impact": "medium"
    }
]

#############################################
# Core Functions
#############################################

def get_frameworks() -> Dict[str, Dict[str, Any]]:
    """
    Get all available regulatory frameworks
    
    Returns:
        Dictionary of all regulatory frameworks
    """
    return REGULATORY_FRAMEWORKS

def get_regulatory_timeline() -> List[Dict[str, Any]]:
    """
    Get the regulatory timeline
    
    Returns:
        List of timeline events
    """
    return REGULATORY_TIMELINE

def is_rag_available() -> bool:
    """
    Check if RAG system is available
    
    Returns:
        Boolean indicating if RAG is available
    """
    return RAG_AVAILABLE

def assess_document_compliance(document_text: str, framework_id: str = "ESRS") -> Dict[str, Any]:
    """
    Comprehensive assessment of a document's compliance with a regulatory framework
    
    Args:
        document_text: Text content of the document to analyze
        framework_id: ID of the regulatory framework to assess against
        
    Returns:
        Detailed compliance assessment results with scores and recommendations
    """
    try:
        # Get the framework details
        frameworks = get_frameworks()
        framework = frameworks.get(framework_id, {})
        
        if not framework:
            logger.warning(f"Framework {framework_id} not found")
            # Use default framework if specified one is not found
            framework_id = next(iter(frameworks.keys()))
            framework = frameworks.get(framework_id, {})
        
        # Extract framework categories
        categories = framework.get('categories', {})
        
        # Generate assessment with AI if available
        if AI_CONNECTOR_AVAILABLE:
            try:
                ai = get_generative_ai()
                
                # Create system prompt for framework assessment
                system_prompt = f"""
                You are an expert in sustainability reporting and regulatory compliance.
                You need to assess a document's compliance with the {framework.get('full_name', framework_id)} framework.
                
                Framework details:
                - Full name: {framework.get('full_name', framework_id)}
                - Description: {framework.get('description', 'No description available')}
                - Categories to assess: {json.dumps(categories)}
                
                Provide a structured assessment with:
                1. Overall compliance score (0-100)
                2. Score for each category (0-100)
                3. Findings for each category
                4. Recommendations for each category
                5. Overall findings and recommendations
                
                Format your response as a JSON object with the following structure:
                {{
                    "framework": "Full framework name",
                    "framework_id": "Framework ID",
                    "date": "Assessment date (ISO format)",
                    "overall_score": "Overall score (0-100)",
                    "categories": {{
                        "category_id": {{
                            "score": "Score for this category (0-100)",
                            "compliance_level": "Compliance level description",
                            "findings": ["Finding 1", "Finding 2"],
                            "recommendations": ["Recommendation 1", "Recommendation 2"]
                        }}
                    }},
                    "overall_findings": ["Finding 1", "Finding 2"],
                    "overall_recommendations": ["Recommendation 1", "Recommendation 2"]
                }}
                """
                
                # Document prompt
                doc_prompt = f"""
                Document to assess:
                
                {document_text[:48000]}  # Truncate to fit model context limits
                
                Assess this document according to the {framework.get('full_name', framework_id)} framework.
                """
                
                # Combine prompts
                full_prompt = f"{system_prompt}\n\n{doc_prompt}"
                
                # Generate response
                ai_response = ai.generate_content(prompt=full_prompt)
                
                # Parse response
                if hasattr(ai_response, 'text'):
                    result = json.loads(ai_response.text)
                elif isinstance(ai_response, dict) and 'text' in ai_response:
                    result = json.loads(ai_response['text'])
                elif isinstance(ai_response, dict):
                    result = ai_response
                else:
                    result = json.loads(str(ai_response))
                
                # Add timestamp if not provided
                if 'date' not in result:
                    result['date'] = datetime.now().isoformat()
                
                return result
            
            except Exception as e:
                logger.error(f"Error using AI for compliance assessment: {str(e)}")
                # Fall back to rules-based assessment
        
        # Fall back to rules-based assessment
        return generate_fallback_assessment(document_text, framework_id)
        
    except Exception as e:
        logger.error(f"Error assessing document compliance: {str(e)}")
        # Return basic assessment with error information
        return {
            "framework": get_frameworks().get(framework_id, {}).get('full_name', framework_id),
            "framework_id": framework_id,
            "date": datetime.now().isoformat(),
            "overall_score": 50,  # Default score
            "categories": {},
            "overall_findings": [f"Error during assessment: {str(e)}"],
            "overall_recommendations": ["Try again with a different document or framework"]
        }

def generate_fallback_assessment(document_text: str, framework_id: str = "ESRS") -> Dict[str, Any]:
    """
    Generate a basic rule-based assessment when AI is not available
    
    Args:
        document_text: Text content of the document
        framework_id: Framework ID
    
    Returns:
        Dictionary with basic assessment
    """
    # Get framework details
    framework = REGULATORY_FRAMEWORKS.get(framework_id, REGULATORY_FRAMEWORKS["ESRS"])
    categories = framework.get("categories", {})
    
    # Simple keyword-based assessment
    results = {
        "framework": framework.get("full_name"),
        "framework_id": framework_id,
        "date": datetime.now().isoformat(),
        "categories": {},
        "overall_findings": [],
        "overall_recommendations": []
    }
    
    # Track total score for averaging
    total_score = 0
    count = 0
    
    # Assess each category
    for category_id, category_name in categories.items():
        # Simple keyword matching (can be enhanced)
        score = 50  # Default score
        
        # Basic scoring logic 
        if category_name.lower() in document_text.lower():
            score += 20
        
        if category_id.lower() in document_text.lower():
            score += 10
        
        # Cap score at 100
        score = min(score, 100)
        
        # Map score to compliance level
        compliance_level = "Unknown"
        if score >= 80:
            compliance_level = "High Compliance"
        elif score >= 60:
            compliance_level = "Medium Compliance"
        elif score >= 40:
            compliance_level = "Low Compliance"
        else:
            compliance_level = "Non-Compliant"
        
        # Add category results
        results["categories"][category_id] = {
            "score": score,
            "compliance_level": compliance_level,
            "findings": [f"Basic keyword analysis for {category_name}"],
            "recommendations": [f"Improve coverage of {category_name}"]
        }
        
        # Update total score
        total_score += score
        count += 1
    
    # Calculate overall score
    results["overall_score"] = round(total_score / max(count, 1))
    
    # Add overall findings and recommendations
    results["overall_findings"] = [
        "Basic assessment completed without AI assistance",
        f"Document appears to cover {len(categories)} categories with varying levels of detail"
    ]
    
    results["overall_recommendations"] = [
        "Consider enhancing coverage of all framework categories",
        "Focus on categories with lower compliance scores"
    ]
    
    return results

def analyze_document_with_rag(document_text: str, query: str, framework_id: str = "ESRS") -> Dict[str, Any]:
    """
    Analyze a document using RAG system with a specific query
    
    Args:
        document_text: Document text
        query: Query to analyze
        framework_id: Framework ID
        
    Returns:
        RAG analysis results
    """
    if not RAG_AVAILABLE:
        logger.warning("RAG system not available, using fallback")
        return {
            "success": False,
            "message": "RAG system not available",
            "fallback_response": "The RAG system is currently unavailable. Please check your Pinecone configuration or try again later."
        }
    
    try:
        # Get framework details
        framework = REGULATORY_FRAMEWORKS.get(framework_id, {})
        
        # Split document into chunks for RAG processing
        chunks = split_document_into_chunks(document_text)
        
        # Get RAG system
        rag_system = get_rag_system()
        
        # Create embeddings for chunks and add to RAG system
        session_id = str(uuid.uuid4())
        
        # Store chunks in RAG system
        for i, chunk in enumerate(chunks):
            embedding = generate_embedding(chunk)
            metadata = {
                "text": chunk,
                "framework": framework_id,
                "chunk_id": i,
                "session_id": session_id
            }
            rag_system.upsert([(f"{session_id}_{i}", embedding, metadata)])
        
        # Query the RAG system
        query_embedding = generate_embedding(query)
        query_results = rag_system.query(
            vector=query_embedding,
            filter={"session_id": session_id},
            top_k=5,
            include_metadata=True
        )
        
        # Process results
        contexts = []
        for match in query_results.matches:
            contexts.append(match.metadata.get("text", ""))
        
        # Generate response with AI
        ai = get_generative_ai()
        prompt = f"""
        CONTEXT INFORMATION:
        {' '.join(contexts)}
        
        QUERY:
        {query}
        
        TASK:
        Based on the regulatory context information, please provide a detailed answer to the query.
        Focus on providing specific information from the document that addresses the query.
        If the context doesn't contain relevant information, state that clearly.
        
        FRAMEWORK:
        {framework.get('full_name', framework_id)}
        """
        
        response = ai.generate_content(prompt)
        
        # Return results
        return {
            "success": True,
            "query": query,
            "framework": framework.get("full_name"),
            "framework_id": framework_id,
            "result": response.text if hasattr(response, "text") else str(response),
            "contexts": contexts,
            "session_id": session_id
        }
        
    except Exception as e:
        logger.error(f"Error in RAG analysis: {str(e)}")
        return {
            "success": False,
            "message": f"Error in RAG analysis: {str(e)}",
            "fallback_response": "An error occurred during document analysis. Please try again or contact support."
        }

def split_document_into_chunks(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
    """
    Split document text into chunks for RAG processing
    
    Args:
        text: Document text
        chunk_size: Size of each chunk
        overlap: Overlap between chunks
        
    Returns:
        List of text chunks
    """
    if not text:
        return []
    
    chunks = []
    start = 0
    
    while start < len(text):
        # Get chunk with specified size
        end = min(start + chunk_size, len(text))
        
        # If not at the end of the text and not at a sentence boundary, find the nearest sentence boundary
        if end < len(text) and text[end] not in ['.', '!', '?', '\n']:
            # Look for the last sentence boundary within the chunk
            last_boundary = max(
                text.rfind('.', start, end),
                text.rfind('!', start, end),
                text.rfind('?', start, end),
                text.rfind('\n', start, end)
            )
            
            # If found a boundary, use it as the end
            if last_boundary > start:
                end = last_boundary + 1
        
        # Add chunk to list
        chunks.append(text[start:end])
        
        # Move start position for next chunk, considering overlap
        start = end - overlap
        
        # Ensure we make progress
        if start >= end:
            start = end
    
    return chunks

#############################################
# Routes
#############################################

@regulatory_ai_bp.route('/')
@regulatory_ai_bp.route('/index')
def regulatory_ai_dashboard():
    """Regulatory AI Agent Dashboard"""
    try:
        logger.info("Starting regulatory_ai_dashboard function")
        
        logger.info("Getting frameworks")
        frameworks = get_frameworks()
        
        logger.info("Getting timeline")
        timeline = get_regulatory_timeline()
        
        # Get parameters from Strategy Hub if passed
        logger.info("Getting request parameters")
        company = request.args.get('company', '')
        industry = request.args.get('industry', '')
        challenges = request.args.get('challenges', '')
        
        # Set pre-filled flag if we have parameters from Strategy Hub
        from_strategy_hub = bool(company and industry)
        logger.info(f"from_strategy_hub: {from_strategy_hub}")
        
        # Check if RAG system is available
        logger.info("Checking RAG system availability")
        rag_system_available = is_rag_available()
        logger.info(f"RAG system available: {rag_system_available}")
        
        # In a real implementation, we would fetch this data from a database
        # For now, we'll use sample data to showcase the dashboard
        logger.info("Creating stats dictionary")
        stats = {
            'documents_count': 12,
            'document_growth': '24%',
            'frameworks_count': 7,
            'recent_framework': 'EU CSRD',
            'avg_compliance': '74%',
            'analysis_count': 48,
            'analysis_growth': '18%'
        }
        
        logger.info("Rendering template")
        return render_template('regulatory/dashboard_refactored.html', 
                            frameworks=frameworks,
                            timeline=timeline,
                            company=company,
                            industry=industry,
                            challenges=challenges,
                            from_strategy_hub=from_strategy_hub,
                            is_rag_available=rag_system_available,
                            page_title="Regulatory AI Agent (Refactored)",
                            active_page="regulatory-ai-refactored",
                            stats=stats,
                            recent_documents=[],  # Use template defaults
                            recent_activity=[])   # Use template defaults
    except Exception as e:
        logger.error(f"Error in regulatory_ai_dashboard: {str(e)}", exc_info=True)
        # Return a simple error page instead of failing completely
        return f"<h1>Error loading dashboard</h1><p>Details: {str(e)}</p>", 500

@regulatory_ai_bp.route('/compliance-visualization')
def compliance_visualization():
    """Regulatory Compliance Visualization Dashboard"""
    frameworks = get_frameworks()
    timeline = get_regulatory_timeline()
    
    return render_template('regulatory/compliance_visualization_page.html',
                          frameworks=frameworks,
                          timeline=timeline,
                          page_title="Compliance Visualization",
                          active_page="regulatory-ai")

@regulatory_ai_bp.route('/document-upload')
def document_upload():
    """Document Upload Page"""
    frameworks = get_frameworks()
    rag_available = is_rag_available()
    
    return render_template('regulatory/document_upload.html',
                          frameworks=frameworks,
                          is_rag_available=rag_available,
                          page_title="Document Upload",
                          active_page="regulatory-ai")

@regulatory_ai_bp.route('/api/assessment', methods=['POST'])
def api_assessment():
    """API endpoint for document assessment"""
    try:
        data = request.json
        document_text = data.get('document_text', '')
        framework_id = data.get('framework_id', 'ESRS')
        
        if not document_text:
            return jsonify({"error": "No document text provided"}), 400
        
        assessment = assess_document_compliance(document_text, framework_id)
        return jsonify(assessment)
    
    except Exception as e:
        logger.error(f"Error in assessment API: {str(e)}")
        return jsonify({"error": str(e)}), 500

@regulatory_ai_bp.route('/api/gap-analysis', methods=['POST'])
def api_gap_analysis():
    """API endpoint for compliance gap analysis"""
    try:
        data = request.json
        document_text = data.get('document_text', '')
        framework_id = data.get('framework_id', 'ESRS')
        assessment_result = data.get('assessment_result', None)
        
        if not document_text and not assessment_result:
            return jsonify({"error": "Either document text or assessment result is required"}), 400
        
        # If assessment result not provided, perform assessment first
        if not assessment_result:
            assessment_result = assess_document_compliance(document_text, framework_id)
        
        # Analyze gaps based on assessment result
        gaps = []
        
        # Find categories with low compliance
        if "categories" in assessment_result:
            for category_id, category_data in assessment_result["categories"].items():
                score = category_data.get("score", 0)
                if score < 60:  # Consider scores below 60 as gaps
                    gaps.append({
                        "category_id": category_id,
                        "category_name": REGULATORY_FRAMEWORKS.get(framework_id, {}).get("categories", {}).get(category_id, "Unknown"),
                        "score": score,
                        "recommendations": category_data.get("recommendations", [])
                    })
        
        return jsonify({
            "framework_id": framework_id,
            "framework_name": REGULATORY_FRAMEWORKS.get(framework_id, {}).get("full_name", framework_id),
            "gaps": gaps,
            "overall_recommendations": assessment_result.get("overall_recommendations", [])
        })
    
    except Exception as e:
        logger.error(f"Error in gap analysis API: {str(e)}")
        return jsonify({"error": str(e)}), 500

@regulatory_ai_bp.route('/api/timeline', methods=['GET'])
def api_timeline():
    """API endpoint for regulatory timeline"""
    return jsonify({
        "timeline": get_regulatory_timeline()
    })

@regulatory_ai_bp.route('/api/frameworks', methods=['GET'])
def api_frameworks():
    """API endpoint for regulatory frameworks"""
    return jsonify({
        "frameworks": get_frameworks()
    })

@regulatory_ai_bp.route('/api/rag-analysis', methods=['POST'])
def api_rag_analysis():
    """API endpoint for RAG-powered document analysis"""
    try:
        data = request.json
        document_text = data.get('document_text', '')
        query = data.get('query', '')
        framework_id = data.get('framework_id', 'ESRS')
        
        if not document_text:
            return jsonify({"error": "No document text provided"}), 400
        
        if not query:
            return jsonify({"error": "No query provided"}), 400
        
        # Perform RAG analysis
        result = analyze_document_with_rag(document_text, query, framework_id)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in RAG analysis API: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@regulatory_ai_bp.route('/api/file-assessment', methods=['POST'])
def api_file_assessment():
    """API endpoint for file upload and assessment"""
    try:
        # Check if file is provided
        if 'file' not in request.files:
            logger.warning("No file part in the request")
            return jsonify({"error": "No file part"}), 400
        
        file = request.files['file']
        
        # Check if file name is empty
        if file.filename == '':
            logger.warning("No file selected for uploading")
            return jsonify({"error": "No file selected"}), 400
        
        # Get framework
        framework_id = request.form.get('framework', 'ESRS')
        
        # Create directory for uploads if it doesn't exist
        os.makedirs('uploads', exist_ok=True)
        
        # Generate unique filename
        filename = str(uuid.uuid4()) + '_' + file.filename
        file_path = os.path.join('uploads', filename)
        
        # Save file
        file.save(file_path)
        logger.info(f"File saved: {file_path}")
        
        # Extract text from file
        document_text = ""
        
        # Simple text extraction based on file extension
        if file_path.lower().endswith('.pdf'):
            try:
                import fitz  # PyMuPDF
                doc = fitz.open(file_path)
                for page in doc:
                    document_text += page.get_text()
                doc.close()
            except ImportError:
                logger.warning("PyMuPDF not available, using fallback")
                try:
                    # Try using a different PDF extraction method
                    import subprocess
                    result = subprocess.run(['pdftotext', file_path, '-'], stdout=subprocess.PIPE, text=True)
                    document_text = result.stdout
                except:
                    return jsonify({"error": "Could not extract text from PDF"}), 500
        elif file_path.lower().endswith('.txt'):
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                document_text = f.read()
        else:
            # For other file types, return error
            return jsonify({"error": "Unsupported file type"}), 400
        
        # Perform assessment
        assessment = assess_document_compliance(document_text, framework_id)
        
        # Return assessment result
        return jsonify({
            "filename": filename,
            "framework": framework_id,
            "assessment": assessment
        })
        
    except Exception as e:
        logger.error(f"Error in file assessment API: {str(e)}")
        return jsonify({
            "error": f"Error processing file: {str(e)}"
        }), 500

@regulatory_ai_bp.route('/api/follow-up-question', methods=['POST'])
def api_follow_up_question():
    """API endpoint for follow-up questions using RAG system"""
    try:
        data = request.json
        session_id = data.get('session_id', '')
        question = data.get('question', '')
        
        if not question:
            return jsonify({"error": "No question provided"}), 400
        
        if not RAG_AVAILABLE:
            return jsonify({
                "success": False,
                "message": "RAG system not available",
                "response": "The RAG system is currently unavailable. Please check your Pinecone configuration or try again later."
            })
        
        try:
            # Get RAG system
            rag_system = get_rag_system()
            
            # Generate embedding for question
            question_embedding = generate_embedding(question)
            
            # Query filter - if session_id provided, use it to filter results
            filter_dict = {"session_id": session_id} if session_id else None
            
            # Query the RAG system
            query_results = rag_system.query(
                vector=question_embedding,
                filter=filter_dict,
                top_k=5,
                include_metadata=True
            )
            
            # Process results
            contexts = []
            for match in query_results.matches:
                contexts.append(match.metadata.get("text", ""))
            
            # Generate response with AI
            ai = get_generative_ai()
            prompt = f"""
            CONTEXT INFORMATION:
            {' '.join(contexts)}
            
            FOLLOW-UP QUESTION:
            {question}
            
            TASK:
            Based on the regulatory context information, please provide a detailed answer to the follow-up question.
            Focus on providing specific information from the document that addresses the question.
            If the context doesn't contain relevant information, state that clearly.
            """
            
            response = ai.generate_content(prompt)
            
            # Return results
            return jsonify({
                "success": True,
                "question": question,
                "response": response.text if hasattr(response, "text") else str(response),
                "contexts": contexts
            })
            
        except Exception as e:
            logger.error(f"Error processing follow-up question: {str(e)}")
            return jsonify({
                "success": False,
                "message": f"Error processing follow-up question: {str(e)}",
                "response": "An error occurred while processing your question. Please try again or contact support."
            })
    
    except Exception as e:
        logger.error(f"Error in follow-up question API: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# Removed unused test route

@regulatory_ai_bp.route('/upload', methods=['GET'])
def upload_page():
    """Document upload page for the Regulatory AI Agent"""
    logger.info("Refactored Regulatory AI Agent upload page accessed")
    return render_template('regulatory/upload_refactored.html')

@regulatory_ai_bp.route('/dashboard', methods=['GET'])
def dashboard_page():
    """Dashboard page for the Regulatory AI Agent"""
    logger.info("Refactored Regulatory AI Agent dashboard page accessed")
    
    # In a real implementation, we would fetch this data from a database
    # For now, we'll use sample data to showcase the dashboard
    stats = {
        'documents_count': 12,
        'document_growth': '24%',
        'frameworks_count': 7,
        'recent_framework': 'EU CSRD',
        'avg_compliance': '74%',
        'analysis_count': 48,
        'analysis_growth': '18%'
    }
    
    return render_template(
        'regulatory/dashboard_refactored.html',
        active_nav='regulatory-ai-refactored',
        page_title="Regulatory AI Dashboard",
        stats=stats,
        recent_documents=[],  # Use template defaults
        recent_activity=[]    # Use template defaults
    )

@regulatory_ai_bp.route('/api/rag-analysis-form', methods=['POST'])
def api_rag_analysis_form():
    """API endpoint for RAG analysis from form data"""
    try:
        # Handle form data
        document_text = request.form.get('document_text', '')
        query = request.form.get('query', '')
        framework_id = request.form.get('framework_id', 'ESRS')
        
        if not document_text:
            return jsonify({"error": "No document text provided"}), 400
        
        if not query:
            return jsonify({"error": "No query provided"}), 400
        
        # Perform RAG analysis
        result = analyze_document_with_rag(document_text, query, framework_id)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in RAG analysis form API: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500