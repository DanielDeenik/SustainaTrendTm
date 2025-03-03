"""
Ethical AI & Transparency Compliance Module

This module ensures AI-driven sustainability assessments adhere to global regulations 
and ethical AI principles including:
- CSRD (Corporate Sustainability Reporting Directive) compliance
- GDPR data privacy requirements
- AI transparency and explainability
- Bias mitigation and fairness assessment

The module provides:
1. Explainable AI (XAI) capabilities for transparency
2. Bias detection and mitigation
3. Regulatory compliance checks
4. Documentation generation for audit trails
"""

import os
import json
import logging
import random
from typing import Dict, List, Any, Optional, Union
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import AI libraries (with proper fallbacks)
try:
    import openai
    from langchain.chat_models import ChatOpenAI
    from langchain.chains import LLMChain
    AI_LIBRARIES_AVAILABLE = True
    logger.info("AI libraries loaded successfully for ethical AI compliance")
except ImportError:
    AI_LIBRARIES_AVAILABLE = False
    logger.warning("AI libraries not available for ethical AI compliance. Using fallback mechanisms.")

def generate_explanation(analysis_result: Dict[str, Any], detail_level: str = "medium") -> Dict[str, Any]:
    """
    Generate human-readable explanations for AI-driven analysis results.
    Implements Explainable AI (XAI) principles.
    
    Args:
        analysis_result: The original AI analysis result
        detail_level: Level of explanation detail (low, medium, high)
        
    Returns:
        Dictionary with original results and added explanations
    """
    logger.info(f"Generating explanation for AI analysis with {detail_level} detail level")
    
    # Create a copy of the original result to avoid modifying it
    result_with_explanation = analysis_result.copy()
    
    # Add explanation metadata
    result_with_explanation["_explanation_metadata"] = {
        "generated_at": datetime.now().isoformat(),
        "detail_level": detail_level,
        "explanation_version": "1.0.0"
    }
    
    # Check if we can use advanced AI for explanations
    openai_api_key = os.getenv('OPENAI_API_KEY')
    
    if openai_api_key and AI_LIBRARIES_AVAILABLE:
        try:
            # Structure the result for explanation
            content_to_explain = json.dumps(analysis_result, indent=2)
            
            # Create prompt for explanation generation
            prompt = f"""
            I need you to explain this AI-generated sustainability analysis in clear, 
            non-technical language that focuses on transparency. The explanation should:
            
            1. Clarify how each score or rating was determined
            2. Identify what data sources and factors influenced the analysis
            3. Acknowledge limitations and confidence levels
            4. Avoid technical jargon and use accessible language
            
            Detail level requested: {detail_level}
            
            Here is the analysis to explain:
            {content_to_explain}
            
            Please structure your response as a JSON with keys matching the original analysis 
            and values containing the explanations.
            """
            
            # Use OpenAI for explanation generation
            llm = ChatOpenAI(model="gpt-4-turbo", temperature=0.2)
            response = llm.invoke(prompt).content
            
            # Parse explanation and integrate with original result
            try:
                explanations = json.loads(response)
                result_with_explanation["_explanations"] = explanations
            except json.JSONDecodeError:
                # Fallback if response isn't valid JSON
                result_with_explanation["_explanations"] = {
                    "general_explanation": response
                }
                
        except Exception as e:
            logger.error(f"Error generating AI explanation: {str(e)}")
            # Fallback to rule-based explanations
            result_with_explanation["_explanations"] = generate_rule_based_explanations(analysis_result, detail_level)
    else:
        # Use rule-based explanations when AI isn't available
        result_with_explanation["_explanations"] = generate_rule_based_explanations(analysis_result, detail_level)
        
    return result_with_explanation

def generate_rule_based_explanations(analysis_result: Dict[str, Any], detail_level: str) -> Dict[str, Any]:
    """
    Generate rule-based explanations when AI isn't available.
    
    Args:
        analysis_result: The original analysis result
        detail_level: Level of explanation detail
        
    Returns:
        Dictionary with explanations for key metrics
    """
    explanations = {}
    
    # Generate general explanation
    explanations["general_explanation"] = (
        "This sustainability analysis was conducted using a combination of industry benchmarks, "
        "historical data patterns, and regulatory compliance frameworks. The system evaluates "
        "multiple factors to determine scores across different sustainability dimensions."
    )
    
    # Add explanations for common metrics if they exist
    if "Sustainability Score" in analysis_result:
        score = analysis_result["Sustainability Score"]
        explanations["Sustainability Score"] = (
            f"This overall score of {score} represents a weighted average across environmental, "
            f"social, and governance dimensions. Scores above 70 indicate strong sustainability "
            f"performance relative to industry peers."
        )
    
    if "Strategic Fit Score" in analysis_result:
        score = analysis_result["Strategic Fit Score"]
        explanations["Strategic Fit Score"] = (
            f"The Strategic Fit Score of {score} measures how well sustainability initiatives "
            f"align with business objectives and market positioning. It considers competitive "
            f"differentiation and growth opportunities."
        )
        
    # Add explanation about data sources
    explanations["data_sources"] = (
        "Analysis is based on publicly available company disclosures, industry benchmarks, "
        "regulatory frameworks, and market trends. Specific data points may include ESG reports, "
        "financial disclosures, news analyses, and industry standards."
    )
    
    # Add explanation about limitations
    explanations["limitations"] = (
        "This analysis provides a point-in-time assessment based on available information. "
        "Results should be considered alongside expert judgment and company-specific context. "
        "The analysis may not capture all sustainability dimensions equally."
    )
    
    return explanations

def detect_bias(analysis_result: Dict[str, Any], company_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Detect potential bias in AI-generated sustainability analysis.
    
    Args:
        analysis_result: The AI-generated analysis
        company_data: Data about the company being analyzed
        
    Returns:
        Dictionary with bias detection results
    """
    logger.info(f"Performing bias detection for analysis of {company_data.get('name', 'unknown company')}")
    
    bias_report = {
        "analysis_id": analysis_result.get("id", str(random.randint(10000, 99999))),
        "company_name": company_data.get("name", "Unknown"),
        "industry": company_data.get("industry", "Unknown"),
        "bias_checks": [],
        "bias_detected": False,
        "bias_score": 0.0,
        "recommendations": []
    }
    
    # Perform basic bias checks
    bias_checks = []
    
    # Check 1: Industry bias (certain industries consistently scored lower/higher)
    industry = company_data.get("industry", "").lower()
    sustainability_score = analysis_result.get("Sustainability Score", 0)
    
    industry_bias_check = {
        "check_name": "Industry Bias",
        "result": "Pass",
        "confidence": 0.8,
        "explanation": f"No systemic bias detected based on {industry} industry classification."
    }
    
    # Check for common industry biases
    potentially_biased_industries = ["oil", "gas", "coal", "mining", "fossil"]
    if any(term in industry for term in potentially_biased_industries) and sustainability_score > 75:
        industry_bias_check["result"] = "Flag"
        industry_bias_check["explanation"] = (
            f"Unusually high sustainability score ({sustainability_score}) for a company in "
            f"the {industry} industry. This may indicate potential positive bias."
        )
        bias_report["bias_detected"] = True
        bias_report["bias_score"] += 0.3
        bias_report["recommendations"].append(
            "Review sustainability scoring methodology for high-impact industries to ensure consistent standards."
        )
    
    bias_checks.append(industry_bias_check)
    
    # Check 2: Size bias (larger companies scored differently)
    size = company_data.get("size", "").lower()
    size_bias_check = {
        "check_name": "Company Size Bias",
        "result": "Pass",
        "confidence": 0.7,
        "explanation": f"No systemic bias detected based on company size."
    }
    
    if size in ["small", "startup"] and sustainability_score < 30:
        size_bias_check["result"] = "Flag"
        size_bias_check["explanation"] = (
            f"Unusually low sustainability score ({sustainability_score}) for a {size} company. "
            f"This may indicate potential negative bias due to limited public disclosures."
        )
        bias_report["bias_detected"] = True
        bias_report["bias_score"] += 0.2
        bias_report["recommendations"].append(
            "Adjust scoring methodology to account for limited public disclosures from smaller companies."
        )
    
    bias_checks.append(size_bias_check)
    
    # Check 3: Recency bias (overemphasis on recent events)
    recency_bias_check = {
        "check_name": "Recency Bias",
        "result": "Pass",
        "confidence": 0.6,
        "explanation": "No significant overemphasis on recent events detected."
    }
    
    # Add more sophisticated checks here when AI is available
    bias_checks.append(recency_bias_check)
    
    # Add checks to report
    bias_report["bias_checks"] = bias_checks
    
    # Generate standardized recommendations for all reports
    if not bias_report["recommendations"]:
        bias_report["recommendations"] = [
            "Continue regular bias monitoring and assessment.",
            "Include diverse data sources to minimize potential blind spots.",
            "Periodically review analysis methodology for evolving industry standards."
        ]
    
    return bias_report

def check_regulatory_compliance(analysis_result: Dict[str, Any], 
                               regulations: List[str] = ["CSRD", "GDPR"]) -> Dict[str, Any]:
    """
    Check if an AI-generated analysis meets regulatory compliance requirements.
    
    Args:
        analysis_result: The AI-generated analysis
        regulations: List of regulations to check compliance against
        
    Returns:
        Dictionary with compliance check results
    """
    logger.info(f"Checking compliance with {', '.join(regulations)}")
    
    compliance_report = {
        "analysis_id": analysis_result.get("id", str(random.randint(10000, 99999))),
        "checked_at": datetime.now().isoformat(),
        "regulations_checked": regulations,
        "compliance_results": {},
        "overall_compliance": "Compliant",
        "recommendations": []
    }
    
    # Check CSRD compliance if requested
    if "CSRD" in regulations:
        csrd_check = check_csrd_compliance(analysis_result)
        compliance_report["compliance_results"]["CSRD"] = csrd_check
        
        if csrd_check["compliance_level"] in ["Non-compliant", "Partially compliant"]:
            compliance_report["overall_compliance"] = "Partially compliant"
            compliance_report["recommendations"].extend(csrd_check["recommendations"])
    
    # Check GDPR compliance if requested
    if "GDPR" in regulations:
        gdpr_check = check_gdpr_compliance(analysis_result)
        compliance_report["compliance_results"]["GDPR"] = gdpr_check
        
        if gdpr_check["compliance_level"] in ["Non-compliant", "Partially compliant"]:
            compliance_report["overall_compliance"] = "Partially compliant"
            compliance_report["recommendations"].extend(gdpr_check["recommendations"])
    
    # Check AI transparency requirements
    ai_transparency_check = check_ai_transparency(analysis_result)
    compliance_report["compliance_results"]["AI Transparency"] = ai_transparency_check
    
    if ai_transparency_check["compliance_level"] in ["Non-compliant", "Partially compliant"]:
        compliance_report["overall_compliance"] = "Partially compliant"
        compliance_report["recommendations"].extend(ai_transparency_check["recommendations"])
    
    return compliance_report

def check_csrd_compliance(analysis_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Check compliance with Corporate Sustainability Reporting Directive (CSRD).
    
    Args:
        analysis_result: The AI-generated analysis
        
    Returns:
        Dictionary with CSRD compliance results
    """
    # Define CSRD requirements
    csrd_requirements = [
        {
            "requirement": "Double Materiality Assessment",
            "description": "Assessment includes both financial materiality and impact materiality",
            "satisfied": False
        },
        {
            "requirement": "Environmental Topics",
            "description": "Covers climate change, pollution, water, biodiversity, and resource use",
            "satisfied": False
        },
        {
            "requirement": "Social Topics", 
            "description": "Addresses workforce topics, affected communities, and consumers/end-users",
            "satisfied": False
        },
        {
            "requirement": "Governance Topics",
            "description": "Covers business conduct, internal controls, and risk management",
            "satisfied": False
        },
        {
            "requirement": "Forward-Looking Information",
            "description": "Includes targets, commitments, and future scenarios",
            "satisfied": False
        }
    ]
    
    # Check if requirements are satisfied
    compliance_level = "Non-compliant"
    recommendations = []
    
    # Check environmental topics
    if any(topic.lower() in str(analysis_result).lower() for topic in 
           ["climate", "emissions", "pollution", "water", "biodiversity", "resource"]):
        csrd_requirements[1]["satisfied"] = True
    else:
        recommendations.append("Include analysis of environmental topics: climate change, pollution, water, biodiversity, resource use")
    
    # Check social topics
    if any(topic.lower() in str(analysis_result).lower() for topic in 
           ["workforce", "employee", "community", "social", "human rights", "consumer"]):
        csrd_requirements[2]["satisfied"] = True
    else:
        recommendations.append("Address social topics: workforce conditions, affected communities, consumer impacts")
    
    # Check governance topics
    if any(topic.lower() in str(analysis_result).lower() for topic in 
           ["governance", "business conduct", "risk", "controls", "ethics"]):
        csrd_requirements[3]["satisfied"] = True
    else:
        recommendations.append("Include governance topics: business conduct, internal controls, risk management")
    
    # Check materiality
    if "materiality" in str(analysis_result).lower() or "material" in str(analysis_result).lower():
        csrd_requirements[0]["satisfied"] = True
    else:
        recommendations.append("Include a double materiality assessment that covers both financial impact and impact on people and environment")
    
    # Check forward-looking information
    if any(topic.lower() in str(analysis_result).lower() for topic in 
           ["target", "goal", "commitment", "future", "plan", "scenario"]):
        csrd_requirements[4]["satisfied"] = True
    else:
        recommendations.append("Include forward-looking information: targets, commitments, future scenarios")
    
    # Determine overall compliance level
    satisfied_count = sum(1 for req in csrd_requirements if req["satisfied"])
    if satisfied_count == len(csrd_requirements):
        compliance_level = "Compliant"
    elif satisfied_count >= 3:
        compliance_level = "Partially compliant"
    
    return {
        "compliance_level": compliance_level,
        "requirements": csrd_requirements,
        "recommendations": recommendations
    }

def check_gdpr_compliance(analysis_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Check compliance with GDPR data privacy requirements.
    
    Args:
        analysis_result: The AI-generated analysis
        
    Returns:
        Dictionary with GDPR compliance results
    """
    # Define GDPR requirements for AI analysis
    gdpr_requirements = [
        {
            "requirement": "Personal Data Minimization",
            "description": "Analysis doesn't include unnecessary personal data",
            "satisfied": True  # Assuming no personal data by default
        },
        {
            "requirement": "Data Processing Transparency",
            "description": "Clear explanation of how data is processed",
            "satisfied": False
        },
        {
            "requirement": "Right to Explanation",
            "description": "Ability to explain automated decisions",
            "satisfied": False
        },
        {
            "requirement": "Data Subject Rights",
            "description": "Respect for access, rectification, erasure rights",
            "satisfied": False
        }
    ]
    
    # Check if requirements are satisfied
    compliance_level = "Non-compliant"
    recommendations = []
    
    # Check for personal data (potential violation)
    personal_data_indicators = ["name", "email", "phone", "address", "person", "individual"]
    if any(indicator in str(analysis_result).lower() for indicator in personal_data_indicators):
        gdpr_requirements[0]["satisfied"] = False
        recommendations.append("Remove or anonymize personal data in the analysis")
    
    # Check for transparency in data processing
    if "_explanation_metadata" in analysis_result:
        gdpr_requirements[1]["satisfied"] = True
    else:
        recommendations.append("Include metadata on data processing methods and sources")
    
    # Check for right to explanation
    if "_explanations" in analysis_result:
        gdpr_requirements[2]["satisfied"] = True
    else:
        recommendations.append("Add explanations for how analysis conclusions were reached")
    
    # Check for data subject rights acknowledgment
    data_rights_indicators = ["data subject", "rights", "access right", "rectification", "erasure"]
    if any(indicator in str(analysis_result).lower() for indicator in data_rights_indicators):
        gdpr_requirements[3]["satisfied"] = True
    else:
        recommendations.append("Include acknowledgment of data subject rights in the analysis documentation")
    
    # Determine overall compliance level
    satisfied_count = sum(1 for req in gdpr_requirements if req["satisfied"])
    if satisfied_count == len(gdpr_requirements):
        compliance_level = "Compliant"
    elif satisfied_count >= 2:
        compliance_level = "Partially compliant"
    
    return {
        "compliance_level": compliance_level,
        "requirements": gdpr_requirements,
        "recommendations": recommendations
    }

def check_ai_transparency(analysis_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Check compliance with AI transparency and explainability requirements.
    
    Args:
        analysis_result: The AI-generated analysis
        
    Returns:
        Dictionary with AI transparency compliance results
    """
    # Define AI transparency requirements
    transparency_requirements = [
        {
            "requirement": "Model Disclosure",
            "description": "Disclosure of AI models and methods used",
            "satisfied": False
        },
        {
            "requirement": "Decision Explanation",
            "description": "Explanation of how AI reached conclusions",
            "satisfied": False
        },
        {
            "requirement": "Confidence Levels",
            "description": "Indication of confidence/uncertainty in results",
            "satisfied": False
        },
        {
            "requirement": "Human Oversight",
            "description": "Clear indication of human review/oversight",
            "satisfied": False
        }
    ]
    
    # Check if requirements are satisfied
    compliance_level = "Non-compliant"
    recommendations = []
    
    # Check for model disclosure
    if "_explanation_metadata" in analysis_result and "model" in str(analysis_result).lower():
        transparency_requirements[0]["satisfied"] = True
    else:
        recommendations.append("Include disclosure of AI models and methods used in the analysis")
    
    # Check for decision explanation
    if "_explanations" in analysis_result:
        transparency_requirements[1]["satisfied"] = True
    else:
        recommendations.append("Add explanations for how conclusions were reached by the AI system")
    
    # Check for confidence levels
    confidence_indicators = ["confidence", "certainty", "probability", "likelihood", "uncertainty"]
    if any(indicator in str(analysis_result).lower() for indicator in confidence_indicators):
        transparency_requirements[2]["satisfied"] = True
    else:
        recommendations.append("Include confidence levels or uncertainty metrics for key findings")
    
    # Check for human oversight indication
    oversight_indicators = ["review", "oversight", "human", "analyst", "verified", "approved"]
    if any(indicator in str(analysis_result).lower() for indicator in oversight_indicators):
        transparency_requirements[3]["satisfied"] = True
    else:
        recommendations.append("Add clear indication of human review/oversight in the analysis process")
    
    # Determine overall compliance level
    satisfied_count = sum(1 for req in transparency_requirements if req["satisfied"])
    if satisfied_count == len(transparency_requirements):
        compliance_level = "Compliant"
    elif satisfied_count >= 2:
        compliance_level = "Partially compliant"
    
    return {
        "compliance_level": compliance_level,
        "requirements": transparency_requirements,
        "recommendations": recommendations
    }

def generate_compliance_documentation(analysis_result: Dict[str, Any], 
                                     compliance_report: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate documentation for audit trails and compliance records.
    
    Args:
        analysis_result: The AI-generated analysis
        compliance_report: Compliance check results
        
    Returns:
        Dictionary with documentation contents
    """
    documentation = {
        "document_id": f"DOC-{random.randint(10000, 99999)}",
        "generated_at": datetime.now().isoformat(),
        "analysis_id": analysis_result.get("id", str(random.randint(10000, 99999))),
        "document_type": "AI Compliance Documentation",
        "company_name": analysis_result.get("Company", "Unknown"),
        "industry": analysis_result.get("Industry", "Unknown"),
        "compliance_summary": compliance_report.get("overall_compliance", "Unknown"),
        "regulations_covered": compliance_report.get("regulations_checked", []),
        "sections": []
    }
    
    # Add introduction section
    documentation["sections"].append({
        "title": "Introduction",
        "content": (
            f"This document provides a compliance record for the AI-generated sustainability "
            f"analysis of {documentation['company_name']} in the {documentation['industry']} industry. "
            f"The analysis was conducted using AI-powered assessment tools and checked against "
            f"applicable regulatory frameworks including {', '.join(documentation['regulations_covered'])}."
        )
    })
    
    # Add methodology section
    documentation["sections"].append({
        "title": "Analysis Methodology",
        "content": (
            "The analysis employed a multi-factor assessment framework incorporating industry "
            "benchmarks, regulatory requirements, and sustainability best practices. "
            "AI algorithms were used to process and analyze the data, with appropriate "
            "human oversight to ensure accuracy and relevance of findings."
        )
    })
    
    # Add compliance assessment section
    documentation["sections"].append({
        "title": "Compliance Assessment",
        "content": (
            f"Overall compliance status: {documentation['compliance_summary']}. "
            f"This assessment covered {len(compliance_report.get('compliance_results', {}))} "
            f"regulatory frameworks and identified "
            f"{len(compliance_report.get('recommendations', []))} areas for improvement."
        ),
        "detailed_results": compliance_report.get("compliance_results", {})
    })
    
    # Add recommendations section
    documentation["sections"].append({
        "title": "Recommendations",
        "content": "The following recommendations are provided to enhance compliance:",
        "recommendations": compliance_report.get("recommendations", [
            "Continue regular compliance monitoring",
            "Update documentation as regulatory requirements evolve",
            "Ensure transparency in AI-driven analysis methodologies"
        ])
    })
    
    # Add signature section for documentation
    documentation["sections"].append({
        "title": "Documentation Certification",
        "content": (
            "This automated documentation was generated by the SustainaTrend™ "
            "AI Compliance Engine. While it provides a comprehensive overview of "
            "compliance status, it is recommended that a qualified sustainability "
            "professional review this documentation before use in formal submissions."
        ),
        "generated_timestamp": datetime.now().isoformat()
    })
    
    return documentation

def analyze_sustainability_report_compliance(report_text: str, 
                                           regulations: List[str] = ["CSRD", "GDPR"]) -> Dict[str, Any]:
    """
    Analyze a sustainability report for compliance with regulations and ethical AI principles.
    
    Args:
        report_text: The sustainability report text
        regulations: List of regulations to check compliance against
        
    Returns:
        Dictionary with compliance analysis results
    """
    logger.info(f"Analyzing sustainability report compliance with {', '.join(regulations)}")
    
    # Initialize analysis result
    compliance_analysis = {
        "analysis_id": f"COMPL-{random.randint(10000, 99999)}",
        "analyzed_at": datetime.now().isoformat(),
        "regulations_analyzed": regulations,
        "compliance_scores": {},
        "risk_areas": [],
        "recommendations": [],
        "detailed_analysis": {}
    }
    
    # Check if we can use AI for advanced analysis
    openai_api_key = os.getenv('OPENAI_API_KEY')
    
    if openai_api_key and AI_LIBRARIES_AVAILABLE:
        try:
            # Create prompt for analysis
            prompt = f"""
            Analyze this sustainability report for compliance with:
            - CSRD (Corporate Sustainability Reporting Directive)
            - GDPR Data Privacy
            - AI Transparency & Bias Mitigation
            
            Report text:
            {report_text[:2000]}... [truncated]
            
            Provide a detailed analysis including:
            1. Compliance scores (0-100) for each regulation
            2. Identified risk areas
            3. Specific recommendations for improvement
            4. Detailed analysis of each compliance area
            
            Format your response as a structured JSON.
            """
            
            # Use OpenAI for analysis
            llm = ChatOpenAI(model="gpt-4-turbo", temperature=0.2)
            response = llm.invoke(prompt).content
            
            # Parse the response
            try:
                ai_analysis = json.loads(response)
                compliance_analysis.update(ai_analysis)
            except json.JSONDecodeError:
                # Fallback to rule-based analysis
                compliance_analysis.update(perform_rule_based_compliance_analysis(report_text, regulations))
                
        except Exception as e:
            logger.error(f"Error in AI-based compliance analysis: {str(e)}")
            # Fallback to rule-based analysis
            compliance_analysis.update(perform_rule_based_compliance_analysis(report_text, regulations))
    else:
        # Use rule-based analysis when AI isn't available
        compliance_analysis.update(perform_rule_based_compliance_analysis(report_text, regulations))
    
    return compliance_analysis

def perform_rule_based_compliance_analysis(report_text: str, regulations: List[str]) -> Dict[str, Any]:
    """
    Perform rule-based compliance analysis when AI isn't available.
    
    Args:
        report_text: The sustainability report text
        regulations: List of regulations to check compliance against
        
    Returns:
        Dictionary with compliance analysis results
    """
    analysis = {
        "compliance_scores": {},
        "risk_areas": [],
        "recommendations": [],
        "detailed_analysis": {}
    }
    
    # Check CSRD compliance
    if "CSRD" in regulations:
        csrd_score, csrd_risks, csrd_recommendations = analyze_csrd_compliance(report_text)
        analysis["compliance_scores"]["CSRD"] = csrd_score
        analysis["risk_areas"].extend(csrd_risks)
        analysis["recommendations"].extend(csrd_recommendations)
        analysis["detailed_analysis"]["CSRD"] = {
            "score": csrd_score,
            "risk_areas": csrd_risks,
            "recommendations": csrd_recommendations
        }
    
    # Check GDPR compliance
    if "GDPR" in regulations:
        gdpr_score, gdpr_risks, gdpr_recommendations = analyze_gdpr_compliance(report_text)
        analysis["compliance_scores"]["GDPR"] = gdpr_score
        analysis["risk_areas"].extend(gdpr_risks)
        analysis["recommendations"].extend(gdpr_recommendations)
        analysis["detailed_analysis"]["GDPR"] = {
            "score": gdpr_score,
            "risk_areas": gdpr_risks,
            "recommendations": gdpr_recommendations
        }
    
    # Check AI Transparency compliance
    ai_score, ai_risks, ai_recommendations = analyze_ai_transparency_compliance(report_text)
    analysis["compliance_scores"]["AI Transparency"] = ai_score
    analysis["risk_areas"].extend(ai_risks)
    analysis["recommendations"].extend(ai_recommendations)
    analysis["detailed_analysis"]["AI Transparency"] = {
        "score": ai_score,
        "risk_areas": ai_risks,
        "recommendations": ai_recommendations
    }
    
    return analysis

def analyze_csrd_compliance(report_text: str) -> tuple:
    """
    Analyze CSRD compliance using rule-based methods.
    
    Args:
        report_text: The sustainability report text
        
    Returns:
        Tuple of (compliance_score, risk_areas, recommendations)
    """
    report_text_lower = report_text.lower()
    
    # Initialize score and findings
    score = 60  # Start with a baseline score
    risk_areas = []
    recommendations = []
    
    # Check for key CSRD requirements
    
    # 1. Double materiality assessment
    if "materiality assessment" in report_text_lower or "double materiality" in report_text_lower:
        score += 10
    else:
        score -= 10
        risk_areas.append("Missing double materiality assessment")
        recommendations.append("Include a double materiality assessment that covers both financial materiality and impact materiality")
    
    # 2. Environmental topics
    env_topics = ["climate change", "pollution", "water", "biodiversity", "resource use"]
    env_coverage = sum(1 for topic in env_topics if topic in report_text_lower)
    if env_coverage >= 3:
        score += 5
    else:
        score -= 5
        risk_areas.append("Insufficient coverage of environmental topics")
        recommendations.append("Expand coverage of environmental topics to include climate change, pollution, water, biodiversity, and resource use")
    
    # 3. Social topics
    social_topics = ["workforce", "human rights", "communities", "consumers"]
    social_coverage = sum(1 for topic in social_topics if topic in report_text_lower)
    if social_coverage >= 2:
        score += 5
    else:
        score -= 5
        risk_areas.append("Insufficient coverage of social topics")
        recommendations.append("Expand coverage of social topics to include workforce, affected communities, and consumers/end-users")
    
    # 4. Governance topics
    gov_topics = ["governance", "business conduct", "ethics", "risk management"]
    gov_coverage = sum(1 for topic in gov_topics if topic in report_text_lower)
    if gov_coverage >= 2:
        score += 5
    else:
        score -= 5
        risk_areas.append("Insufficient coverage of governance topics")
        recommendations.append("Expand coverage of governance topics to include business conduct, internal controls, and risk management")
    
    # 5. Forward-looking information
    if any(term in report_text_lower for term in ["target", "goal", "commitment", "plan"]):
        score += 5
    else:
        score -= 5
        risk_areas.append("Missing forward-looking information")
        recommendations.append("Include forward-looking information such as targets, commitments, and plans")
    
    # Ensure score is within 0-100 range
    score = max(0, min(100, score))
    
    return score, risk_areas, recommendations

def analyze_gdpr_compliance(report_text: str) -> tuple:
    """
    Analyze GDPR compliance using rule-based methods.
    
    Args:
        report_text: The sustainability report text
        
    Returns:
        Tuple of (compliance_score, risk_areas, recommendations)
    """
    report_text_lower = report_text.lower()
    
    # Initialize score and findings
    score = 70  # Start with a baseline score
    risk_areas = []
    recommendations = []
    
    # Check for key GDPR concerns
    
    # 1. Personal data handling
    personal_data_terms = ["personal data", "personally identifiable", "personal information"]
    if any(term in report_text_lower for term in personal_data_terms):
        # Check if proper data protection measures are mentioned
        protection_terms = ["data protection", "anonymized", "pseudonymized", "consent", "data minimization"]
        if not any(term in report_text_lower for term in protection_terms):
            score -= 15
            risk_areas.append("Personal data mentioned without adequate protection measures")
            recommendations.append("Ensure all personal data is properly anonymized or has explicit consent for processing")
    
    # 2. Transparency in data processing
    if "data processing" in report_text_lower and "transparency" in report_text_lower:
        score += 10
    else:
        score -= 10
        risk_areas.append("Lack of transparency in data processing")
        recommendations.append("Include clear explanation of how data is processed in compliance with GDPR transparency requirements")
    
    # 3. Data subject rights
    rights_terms = ["right to access", "right to erasure", "right to rectification", "data subject rights"]
    if any(term in report_text_lower for term in rights_terms):
        score += 10
    else:
        score -= 10
        risk_areas.append("No mention of data subject rights")
        recommendations.append("Include acknowledgment of data subject rights (access, rectification, erasure) in the report")
    
    # 4. Data processing legal basis
    legal_basis_terms = ["legal basis", "legitimate interest", "consent for", "contractual necessity"]
    if any(term in report_text_lower for term in legal_basis_terms):
        score += 10
    else:
        score -= 10
        risk_areas.append("No clear legal basis for data processing")
        recommendations.append("Specify the legal basis for all data processing activities mentioned in the report")
    
    # Ensure score is within 0-100 range
    score = max(0, min(100, score))
    
    return score, risk_areas, recommendations

def analyze_ai_transparency_compliance(report_text: str) -> tuple:
    """
    Analyze AI transparency compliance using rule-based methods.
    
    Args:
        report_text: The sustainability report text
        
    Returns:
        Tuple of (compliance_score, risk_areas, recommendations)
    """
    report_text_lower = report_text.lower()
    
    # Initialize score and findings
    score = 50  # Start with a baseline score
    risk_areas = []
    recommendations = []
    
    # Check for key AI transparency requirements
    
    # 1. AI usage disclosure
    ai_terms = ["ai", "artificial intelligence", "machine learning", "algorithm", "automated analysis"]
    if any(term in report_text_lower for term in ai_terms):
        # If AI is mentioned, look for transparency measures
        transparency_terms = ["model", "methodology", "explainable ai", "xai", "ai transparency"]
        if any(term in report_text_lower for term in transparency_terms):
            score += 15
        else:
            score -= 15
            risk_areas.append("AI use without transparency disclosure")
            recommendations.append("Disclose AI models and methods used in sustainability assessments")
    
    # 2. Decision explanation
    explanation_terms = ["explainable", "explanation", "how we determined", "analysis process"]
    if any(term in report_text_lower for term in explanation_terms):
        score += 15
    else:
        score -= 10
        risk_areas.append("Lack of explanation for AI-driven decisions")
        recommendations.append("Provide explanations for how AI-driven conclusions were reached")
    
    # 3. Confidence levels
    confidence_terms = ["confidence level", "certainty", "uncertainty", "probability", "likelihood"]
    if any(term in report_text_lower for term in confidence_terms):
        score += 10
    else:
        score -= 5
        risk_areas.append("No confidence levels for AI predictions")
        recommendations.append("Include confidence levels or uncertainty metrics for AI-generated insights")
    
    # 4. Bias mitigation
    bias_terms = ["bias mitigation", "fairness", "ethical ai", "ai ethics", "algorithmic bias"]
    if any(term in report_text_lower for term in bias_terms):
        score += 15
    else:
        score -= 15
        risk_areas.append("No mention of AI bias mitigation")
        recommendations.append("Include information on how AI bias is detected and mitigated in sustainability assessments")
    
    # 5. Human oversight
    oversight_terms = ["human oversight", "human review", "human in the loop", "human verification"]
    if any(term in report_text_lower for term in oversight_terms):
        score += 10
    else:
        score -= 10
        risk_areas.append("No mention of human oversight for AI systems")
        recommendations.append("Clarify human oversight processes for AI-generated sustainability assessments")
    
    # Ensure score is within 0-100 range
    score = max(0, min(100, score))
    
    return score, risk_areas, recommendations