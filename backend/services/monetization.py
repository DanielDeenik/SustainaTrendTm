from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
import os
import json
import random

def monetize_data(company_name):
    """
    Generate monetization strategies for sustainability data
    """
    try:
        prompt = f"""
        Create a comprehensive data monetization strategy for '{company_name}' focused on sustainability data:
        
        1. Identify valuable sustainability data assets the company likely has
        2. Propose monetization models (direct, indirect, and data-as-a-service)
        3. Evaluate market potential and revenue opportunities
        4. Recommend implementation steps with timeline
        
        Format the response as a structured JSON with the following sections:
        {{
            "Data Assets": [
                {{
                    "Asset": "...",
                    "Value Proposition": "...",
                    "Potential Customers": ["...", "..."]
                }},
                ...
            ],
            "Monetization Models": [
                {{
                    "Model": "...",
                    "Description": "...",
                    "Revenue Potential": "...",
                    "Implementation Complexity": "..."
                }},
                ...
            ],
            "Market Analysis": {{
                "Total Addressable Market": "...",
                "Competitive Landscape": "...",
                "Growth Trends": "..."
            }},
            "Implementation Roadmap": [
                {{
                    "Phase": "...",
                    "Activities": ["...", "..."],
                    "Timeline": "...",
                    "Expected Outcomes": "..."
                }},
                ...
            ]
        }}
        """
        
        # Check if OpenAI API key is available
        openai_api_key = os.getenv('OPENAI_API_KEY')
        if not openai_api_key:
            # Return mock data if API key is not available
            return generate_mock_monetization_strategy(company_name)
            
        # Use OpenAI for analysis
        llm = ChatOpenAI(model="gpt-4-turbo", temperature=0.3)
        response = RetrievalQA.from_chain_type(llm, chain_type="stuff").run(prompt)
        
        # Try to parse the response as JSON, fall back to mock data if parsing fails
        try:
            return json.loads(response)
        except:
            return generate_mock_monetization_strategy(company_name)
            
    except Exception as e:
        print(f"Error in data monetization: {str(e)}")
        return generate_mock_monetization_strategy(company_name)

def generate_mock_monetization_strategy(company_name):
    """Generate mock data for monetization strategy when API is unavailable"""
    return {
        "Data Assets": [
            {
                "Asset": "Carbon Emissions Data",
                "Value Proposition": "Granular, verified emissions data across operations and supply chain",
                "Potential Customers": ["ESG Rating Agencies", "Sustainability Consultants", "Carbon Offset Developers"]
            },
            {
                "Asset": "Energy Efficiency Metrics",
                "Value Proposition": "Detailed energy consumption patterns and optimization insights",
                "Potential Customers": ["Energy Service Companies", "Facility Managers", "Sustainability Researchers"]
            },
            {
                "Asset": "Supply Chain Sustainability Scores",
                "Value Proposition": "Comprehensive sustainability assessments of supply chain partners",
                "Potential Customers": ["Procurement Teams", "Supply Chain Consultants", "ESG Investors"]
            }
        ],
        "Monetization Models": [
            {
                "Model": "Sustainability Data Marketplace",
                "Description": f"Platform where {company_name} sells anonymized, aggregated sustainability data sets",
                "Revenue Potential": "$2-5M annually",
                "Implementation Complexity": "High"
            },
            {
                "Model": "Sustainability Analytics-as-a-Service",
                "Description": "Subscription service providing insights and benchmarking from sustainability data",
                "Revenue Potential": "$3-7M annually",
                "Implementation Complexity": "Medium"
            },
            {
                "Model": "ESG Reporting Automation",
                "Description": "Tools for automating ESG data collection, verification, and reporting",
                "Revenue Potential": "$1-3M annually",
                "Implementation Complexity": "Low"
            }
        ],
        "Market Analysis": {
            "Total Addressable Market": "$4.5B globally for sustainability data services",
            "Competitive Landscape": "Emerging market with mix of startups and established sustainability consultancies",
            "Growth Trends": "25-30% annual growth expected in sustainability data services market"
        },
        "Implementation Roadmap": [
            {
                "Phase": "Data Asset Inventory & Preparation",
                "Activities": ["Audit available data", "Establish data governance", "Develop data quality standards"],
                "Timeline": "3-6 months",
                "Expected Outcomes": "Complete inventory of monetizable data assets with quality assessment"
            },
            {
                "Phase": "Pilot Monetization Program",
                "Activities": ["Select highest-potential model", "Develop minimal viable product", "Engage early customers"],
                "Timeline": "6-9 months",
                "Expected Outcomes": "First revenue from data monetization, validated value proposition"
            },
            {
                "Phase": "Scale & Expand",
                "Activities": ["Enhance data product features", "Expand customer base", "Develop additional monetization models"],
                "Timeline": "9-18 months",
                "Expected Outcomes": "Established data monetization program with multiple revenue streams"
            }
        ]
    }
