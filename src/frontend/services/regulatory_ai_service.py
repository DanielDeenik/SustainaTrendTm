"""
Regulatory AI Service Module for SustainaTrend™

This module provides shared AI-powered regulatory compliance functionality
used by both the original and refactored Regulatory AI Agent modules.

Key features:
1. Regulatory framework assessment across multiple jurisdictions
2. AI-powered compliance gap analysis
3. Timeline recommendations for regulatory transitions
4. Visual compliance reporting dashboard
"""

import json
import logging
import os
import sys
import uuid
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

# Set up logging
logger = logging.getLogger(__name__)

# Import AI connector if available
try:
    from frontend.services.ai_connector import (
        connect_to_ai_services,
        generate_embedding,
        semantic_search,
        get_completion,
        is_pinecone_available
    )
    logger.info("AI connector module loaded successfully")
    # Check if Pinecone is available
    pinecone_status = "Connected" if is_pinecone_available() else "Not connected"
    logger.info(f"Pinecone RAG system availability: {pinecone_status}")
except ImportError as e:
    logger.warning(f"AI connector not available: {e}")
    # Create stub functions for development
    def connect_to_ai_services(): return False
    def generate_embedding(text): return [0.0] * 1536  # Mock embedding
    def semantic_search(query, top_k=5): return []
    def get_completion(prompt): return {"text": "AI completion not available"}
    def is_pinecone_available(): return False
    pinecone_status = "Not available"

# List of supported regulatory frameworks
SUPPORTED_FRAMEWORKS = {
    "CSRD": "Corporate Sustainability Reporting Directive",
    "ESRS": "European Sustainability Reporting Standards",
    "SFDR": "Sustainable Finance Disclosure Regulation",
    "TCFD": "Task Force on Climate-related Financial Disclosures",
    "GRI": "Global Reporting Initiative",
    "SASB": "Sustainability Accounting Standards Board",
    "ISSB": "International Sustainability Standards Board",
    "EU_TAXONOMY": "EU Taxonomy for Sustainable Activities",
    "CDP": "Carbon Disclosure Project",
    "SDG": "Sustainable Development Goals",
    "IIRC": "International Integrated Reporting Council",
    "ISO26000": "ISO 26000 Social Responsibility"
}

# Mapping of frameworks to their regulatory jurisdictions
FRAMEWORK_JURISDICTIONS = {
    "CSRD": "European Union",
    "ESRS": "European Union",
    "SFDR": "European Union",
    "TCFD": "Global/Multiple",
    "GRI": "Global/Multiple",
    "SASB": "Global/Multiple",
    "ISSB": "Global/Multiple",
    "EU_TAXONOMY": "European Union",
    "CDP": "Global/Multiple",
    "SDG": "Global/Multiple",
    "IIRC": "Global/Multiple",
    "ISO26000": "Global/Multiple"
}

# Document upload directory
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def get_supported_frameworks() -> Dict[str, str]:
    """
    Get the list of supported regulatory frameworks
    
    Returns:
        Dict[str, str]: Dictionary of framework IDs and names
    """
    return SUPPORTED_FRAMEWORKS

def analyze_document_compliance(
    document_text: str, 
    frameworks: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Analyze a document for compliance with specified regulatory frameworks
    
    Args:
        document_text: Text content of the document
        frameworks: List of framework IDs to check against (default: all supported frameworks)
        
    Returns:
        Dict[str, Any]: Compliance analysis results
    """
    if not frameworks:
        frameworks = list(SUPPORTED_FRAMEWORKS.keys())
    
    # Validate frameworks
    frameworks = [f for f in frameworks if f in SUPPORTED_FRAMEWORKS]
    
    # Prepare results structure
    results = {
        "timestamp": datetime.now().isoformat(),
        "document_length": len(document_text),
        "frameworks_analyzed": len(frameworks),
        "summary": "",
        "frameworks": {}
    }
    
    # Use AI to analyze compliance if available, otherwise use rules-based approach
    if is_pinecone_available():
        return _analyze_with_ai(document_text, frameworks)
    else:
        return _analyze_with_rules(document_text, frameworks)

def _analyze_with_ai(document_text: str, frameworks: List[str]) -> Dict[str, Any]:
    """
    Analyze document compliance using AI
    
    Args:
        document_text: Document text
        frameworks: List of frameworks to check
        
    Returns:
        Dict[str, Any]: Compliance analysis results
    """
    # Generate embedding for the document
    try:
        text_chunks = _chunk_document(document_text)
        embeddings = [generate_embedding(chunk) for chunk in text_chunks[:5]]  # Limit to 5 chunks for performance
        
        # For each framework, evaluate compliance using AI
        results = {
            "timestamp": datetime.now().isoformat(),
            "document_length": len(document_text),
            "frameworks_analyzed": len(frameworks),
            "frameworks": {}
        }
        
        # Generate overall summary
        summary_prompt = f"""
        Analyze the following sustainability report excerpt for compliance with key regulatory frameworks:
        
        {text_chunks[0][:1500]}
        
        Provide a brief summary of the document's overall regulatory compliance approach:
        """
        
        summary_response = get_completion(summary_prompt)
        results["summary"] = summary_response.get("text", "Summary generation failed")
        
        # Analyze each framework
        for framework in frameworks:
            framework_results = _analyze_framework_compliance(document_text, framework)
            results["frameworks"][framework] = framework_results
        
        return results
    except Exception as e:
        logger.error(f"Error in AI-based compliance analysis: {str(e)}")
        # Fall back to rules-based analysis
        return _analyze_with_rules(document_text, frameworks)

def _analyze_with_rules(document_text: str, frameworks: List[str]) -> Dict[str, Any]:
    """
    Analyze document compliance using rule-based approach
    
    Args:
        document_text: Document text
        frameworks: List of frameworks to check
        
    Returns:
        Dict[str, Any]: Compliance analysis results
    """
    # Lower case for easier matching
    text_lower = document_text.lower()
    
    # Prepare results structure
    results = {
        "timestamp": datetime.now().isoformat(),
        "document_length": len(document_text),
        "frameworks_analyzed": len(frameworks),
        "summary": "This analysis was performed using keyword matching since AI services are not available.",
        "frameworks": {}
    }
    
    # Framework-specific keywords for detecting mentions
    framework_keywords = {
        "CSRD": ["csrd", "corporate sustainability reporting directive"],
        "ESRS": ["esrs", "european sustainability reporting standards"],
        "SFDR": ["sfdr", "sustainable finance disclosure regulation"],
        "TCFD": ["tcfd", "task force on climate", "climate-related financial disclosures"],
        "GRI": ["gri", "global reporting initiative"],
        "SASB": ["sasb", "sustainability accounting standards board"],
        "ISSB": ["issb", "international sustainability standards board"],
        "EU_TAXONOMY": ["eu taxonomy", "taxonomy regulation", "sustainable activities"],
        "CDP": ["cdp", "carbon disclosure project"],
        "SDG": ["sdg", "sustainable development goal"],
        "IIRC": ["iirc", "integrated reporting", "international integrated reporting"],
        "ISO26000": ["iso 26000", "iso26000", "social responsibility standard"]
    }
    
    # Check each framework
    for framework in frameworks:
        keywords = framework_keywords.get(framework, [framework.lower()])
        
        # Count keyword mentions
        mentions = sum(text_lower.count(keyword) for keyword in keywords)
        
        # Check for compliance statements
        compliance_terms = [
            f"compliant with {framework.lower()}", 
            f"compliance with {framework.lower()}",
            f"adheres to {framework.lower()}",
            f"follows {framework.lower()}",
            f"accordance with {framework.lower()}"
        ]
        compliance_statements = sum(text_lower.count(term) for term in compliance_terms)
        
        # Calculate compliance score (simple heuristic)
        # 0.0 = No mentions, 0.5 = Some mentions, 1.0 = Explicit compliance statements
        if compliance_statements > 0:
            compliance_score = min(1.0, 0.5 + (compliance_statements * 0.1))
        elif mentions > 0:
            compliance_score = min(0.5, 0.1 + (mentions * 0.05))
        else:
            compliance_score = 0.0
        
        # Create framework result
        framework_result = {
            "framework_id": framework,
            "framework_name": SUPPORTED_FRAMEWORKS.get(framework, framework),
            "jurisdiction": FRAMEWORK_JURISDICTIONS.get(framework, "Global/Multiple"),
            "compliance_score": compliance_score,
            "compliance_level": _score_to_level(compliance_score),
            "mentions": mentions,
            "explicit_statements": compliance_statements,
            "findings": _generate_findings(framework, compliance_score, mentions),
            "recommendations": _generate_recommendations(framework, compliance_score)
        }
        
        results["frameworks"][framework] = framework_result
    
    # Calculate overall compliance score (average across frameworks)
    framework_scores = [results["frameworks"][f]["compliance_score"] for f in frameworks]
    results["overall_score"] = sum(framework_scores) / len(framework_scores) if framework_scores else 0.0
    results["overall_level"] = _score_to_level(results["overall_score"])
    
    return results

def _analyze_framework_compliance(document_text: str, framework: str) -> Dict[str, Any]:
    """
    Analyze compliance with a specific framework using AI
    
    Args:
        document_text: Document text
        framework: Framework ID
        
    Returns:
        Dict[str, Any]: Framework compliance results
    """
    # Extract key sections from document for analysis
    text_chunks = _chunk_document(document_text)
    representative_text = "\n\n".join(text_chunks[:3])  # Use first 3 chunks
    
    # Create analysis prompt for the framework
    prompt = f"""
    Analyze the following sustainability report excerpt for compliance with {SUPPORTED_FRAMEWORKS.get(framework, framework)}:
    
    {representative_text[:2500]}
    
    Provide a detailed analysis in JSON format with the following structure:
    {{
        "compliance_score": [number between 0 and 1],
        "compliance_level": [one of: "Non-compliant", "Partially compliant", "Mostly compliant", "Fully compliant"],
        "key_findings": [list of key findings],
        "gaps": [list of compliance gaps],
        "recommendations": [list of recommendations]
    }}
    
    Focus on substantive compliance, not just mentions of the framework.
    """
    
    try:
        response = get_completion(prompt)
        result_text = response.get("text", "{}")
        
        # Extract JSON part from response
        try:
            # Try to find JSON block in the response
            json_start = result_text.find('{')
            json_end = result_text.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                json_str = result_text[json_start:json_end]
                analysis_result = json.loads(json_str)
            else:
                # Fallback if JSON parsing fails
                analysis_result = json.loads(result_text)
        except json.JSONDecodeError:
            # Create a result if JSON parsing fails
            analysis_result = {
                "compliance_score": 0.5,
                "compliance_level": "Partially compliant",
                "key_findings": ["JSON parsing error in AI response"],
                "gaps": ["Unable to determine specific gaps due to AI response format"],
                "recommendations": ["Retry analysis or use manual assessment"]
            }
        
        # Ensure result has all required fields
        if "compliance_score" not in analysis_result:
            analysis_result["compliance_score"] = 0.5
        if "compliance_level" not in analysis_result:
            analysis_result["compliance_level"] = _score_to_level(analysis_result["compliance_score"])
        
        # Add framework metadata
        framework_result = {
            "framework_id": framework,
            "framework_name": SUPPORTED_FRAMEWORKS.get(framework, framework),
            "jurisdiction": FRAMEWORK_JURISDICTIONS.get(framework, "Global/Multiple"),
            "compliance_score": analysis_result.get("compliance_score", 0.5),
            "compliance_level": analysis_result.get("compliance_level", "Partially compliant"),
            "findings": analysis_result.get("key_findings", []),
            "gaps": analysis_result.get("gaps", []),
            "recommendations": analysis_result.get("recommendations", [])
        }
        
        return framework_result
    except Exception as e:
        logger.error(f"Error analyzing framework compliance with AI: {str(e)}")
        # Fallback to simple result
        return {
            "framework_id": framework,
            "framework_name": SUPPORTED_FRAMEWORKS.get(framework, framework),
            "jurisdiction": FRAMEWORK_JURISDICTIONS.get(framework, "Global/Multiple"),
            "compliance_score": 0.3,
            "compliance_level": "Partially compliant",
            "findings": ["Error during AI analysis"],
            "gaps": ["Unable to determine specific gaps due to AI error"],
            "recommendations": ["Retry analysis or use manual assessment"]
        }

def _chunk_document(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
    """
    Split document into overlapping chunks for processing
    
    Args:
        text: Document text
        chunk_size: Size of each chunk
        overlap: Overlap between chunks
        
    Returns:
        List[str]: List of text chunks
    """
    # Split into paragraphs first
    paragraphs = text.split('\n\n')
    
    chunks = []
    current_chunk = ""
    
    for paragraph in paragraphs:
        # If adding this paragraph exceeds the chunk size, save the current chunk and start a new one
        if len(current_chunk) + len(paragraph) > chunk_size and current_chunk:
            chunks.append(current_chunk)
            # Start new chunk with overlap from the end of the previous chunk
            # Split by words to avoid cutting in the middle of a word
            words = current_chunk.split()
            overlap_words = words[-min(50, len(words)):]  # Take up to 50 words for overlap
            current_chunk = ' '.join(overlap_words) + '\n\n' + paragraph
        else:
            # Add paragraph to current chunk
            if current_chunk:
                current_chunk += '\n\n'
            current_chunk += paragraph
    
    # Add the last chunk if not empty
    if current_chunk:
        chunks.append(current_chunk)
    
    return chunks

def _score_to_level(score: float) -> str:
    """
    Convert numerical compliance score to text level
    
    Args:
        score: Compliance score (0.0 to 1.0)
        
    Returns:
        str: Compliance level description
    """
    if score < 0.25:
        return "Non-compliant"
    elif score < 0.5:
        return "Partially compliant"
    elif score < 0.75:
        return "Mostly compliant"
    else:
        return "Fully compliant"

def _generate_findings(framework: str, score: float, mentions: int) -> List[str]:
    """
    Generate findings based on framework and score
    
    Args:
        framework: Framework ID
        score: Compliance score
        mentions: Number of framework mentions
        
    Returns:
        List[str]: Generated findings
    """
    findings = []
    
    if score < 0.25:
        findings.append(f"Document shows minimal or no evidence of {framework} compliance")
        if mentions == 0:
            findings.append(f"No mentions of {framework} found in document")
        else:
            findings.append(f"Limited mentions of {framework} ({mentions} instances) without substantive compliance evidence")
    elif score < 0.5:
        findings.append(f"Document shows some awareness of {framework} requirements")
        findings.append(f"Partial evidence of {framework} compliance found")
    elif score < 0.75:
        findings.append(f"Document demonstrates significant alignment with {framework} requirements")
        findings.append(f"Most key {framework} elements are addressed")
    else:
        findings.append(f"Document demonstrates comprehensive compliance with {framework} requirements")
        findings.append(f"All key {framework} elements appear to be addressed")
    
    return findings

def _generate_recommendations(framework: str, score: float) -> List[str]:
    """
    Generate recommendations based on framework and score
    
    Args:
        framework: Framework ID
        score: Compliance score
        
    Returns:
        List[str]: Generated recommendations
    """
    recommendations = []
    
    if score < 0.25:
        recommendations.append(f"Develop a comprehensive {framework} compliance strategy")
        recommendations.append(f"Consult with {framework} compliance experts")
        recommendations.append("Implement dedicated ESG reporting processes")
    elif score < 0.5:
        recommendations.append(f"Enhance current {framework} compliance approach")
        recommendations.append("Strengthen disclosure of material sustainability topics")
        recommendations.append("Implement more robust data collection processes")
    elif score < 0.75:
        recommendations.append("Address remaining compliance gaps")
        recommendations.append("Enhance quantitative metrics and targets")
        recommendations.append("Consider external assurance for sustainability reporting")
    else:
        recommendations.append("Maintain current compliance level")
        recommendations.append("Monitor for regulatory updates and changes")
        recommendations.append("Consider leadership opportunities in sustainability reporting")
    
    return recommendations

def generate_compliance_visualization_data(analysis_results: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate data for compliance visualization dashboard
    
    Args:
        analysis_results: Results from analyze_document_compliance
        
    Returns:
        Dict[str, Any]: Visualization data
    """
    visualization_data = {
        "overall_score": analysis_results.get("overall_score", 0.0),
        "overall_level": analysis_results.get("overall_level", "Non-compliant"),
        "frameworks": [],
        "jurisdictions": {},
        "recommendations": []
    }
    
    # Process each framework
    for framework_id, framework_data in analysis_results.get("frameworks", {}).items():
        # Add framework to visualization data
        framework_item = {
            "id": framework_id,
            "name": framework_data.get("framework_name", framework_id),
            "score": framework_data.get("compliance_score", 0.0),
            "level": framework_data.get("compliance_level", "Non-compliant"),
            "jurisdiction": framework_data.get("jurisdiction", "Global/Multiple")
        }
        
        visualization_data["frameworks"].append(framework_item)
        
        # Add to jurisdiction grouping
        jurisdiction = framework_data.get("jurisdiction", "Global/Multiple")
        if jurisdiction not in visualization_data["jurisdictions"]:
            visualization_data["jurisdictions"][jurisdiction] = {
                "frameworks": [],
                "average_score": 0.0
            }
        
        visualization_data["jurisdictions"][jurisdiction]["frameworks"].append({
            "id": framework_id,
            "name": framework_data.get("framework_name", framework_id),
            "score": framework_data.get("compliance_score", 0.0)
        })
        
        # Add unique recommendations
        for rec in framework_data.get("recommendations", []):
            if rec not in visualization_data["recommendations"]:
                visualization_data["recommendations"].append(rec)
    
    # Calculate jurisdiction averages
    for jurisdiction, data in visualization_data["jurisdictions"].items():
        scores = [f["score"] for f in data["frameworks"]]
        data["average_score"] = sum(scores) / len(scores) if scores else 0.0
        data["framework_count"] = len(data["frameworks"])
    
    # Add timeline guidance based on jurisdictions
    visualization_data["timeline"] = _generate_compliance_timeline(visualization_data["jurisdictions"])
    
    return visualization_data

def _generate_compliance_timeline(jurisdictions: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Generate compliance timeline guidance
    
    Args:
        jurisdictions: Jurisdiction data from visualization
        
    Returns:
        List[Dict[str, Any]]: Timeline events
    """
    timeline = []
    current_year = datetime.now().year
    
    # EU timeline events - only add if EU jurisdictions are present
    if "European Union" in jurisdictions:
        timeline.extend([
            {
                "date": f"{current_year}-06-30",
                "title": "CSRD First Reports Due",
                "description": "Large companies covered in first wave of CSRD must publish their first reports.",
                "jurisdiction": "European Union"
            },
            {
                "date": f"{current_year + 1}-06-30",
                "title": "CSRD Second Wave",
                "description": "Medium-sized companies must publish their first CSRD reports.",
                "jurisdiction": "European Union"
            },
            {
                "date": f"{current_year}-03-31",
                "title": "SFDR Annual Update",
                "description": "Annual update of entity-level SFDR disclosures required.",
                "jurisdiction": "European Union"
            }
        ])
    
    # Global timeline events
    timeline.extend([
        {
            "date": f"{current_year}-12-31",
            "title": "TCFD Reporting",
            "description": "Recommended deadline for annual TCFD disclosures.",
            "jurisdiction": "Global/Multiple"
        },
        {
            "date": f"{current_year}-08-31",
            "title": "CDP Submission Deadline",
            "description": "Typical deadline for CDP climate change questionnaire.",
            "jurisdiction": "Global/Multiple"
        }
    ])
    
    # Sort timeline by date
    timeline.sort(key=lambda x: x["date"])
    
    return timeline

def handle_document_upload(file) -> Tuple[bool, str, Optional[str]]:
    """
    Handle document upload and processing
    
    Args:
        file: Uploaded file object
        
    Returns:
        Tuple of (success, message, file_id)
    """
    try:
        # Generate a unique filename
        file_id = str(uuid.uuid4())
        filename = file_id + '_' + file.filename
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        
        # Save the file
        file.save(file_path)
        
        # Return success response
        return True, "Document uploaded successfully", file_id
    except Exception as e:
        logger.error(f"Error handling document upload: {str(e)}")
        return False, f"Error uploading document: {str(e)}", None

def get_upload_folder() -> str:
    """
    Get the path to the upload folder
    
    Returns:
        str: Path to upload folder
    """
    return UPLOAD_FOLDER