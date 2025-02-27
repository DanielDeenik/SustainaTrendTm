"""
AI-Powered Sustainability Storytelling Service
Uses LangChain and OpenAI to generate strategic narratives for sustainability
that align with McKinsey frameworks and provide investment and monetization pathways.
"""
import os
import json
import logging
from datetime import datetime
import random

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import LangChain components, but provide fallbacks if not available
try:
    from langchain.chat_models import ChatOpenAI
    from langchain.chains import RetrievalQA
    LANGCHAIN_AVAILABLE = True
except ImportError:
    logger.warning("LangChain not available. Using mock storytelling.")
    LANGCHAIN_AVAILABLE = False

def generate_sustainability_story(company_name, industry):
    """
    Generate an AI-powered sustainability transformation story
    
    Args:
        company_name (str): Name of the company
        industry (str): Industry the company operates in
        
    Returns:
        dict: Structured sustainability story with strategy, monetization model,
              investment pathway, and actionable recommendations
    """
    logger.info(f"Generating sustainability story for {company_name} in {industry} industry")
    
    # Check if OpenAI API key is available
    openai_api_key = os.getenv('OPENAI_API_KEY')
    
    if openai_api_key and LANGCHAIN_AVAILABLE:
        try:
            # Use LangChain and OpenAI to generate the story
            prompt = f"""
            Create an **AI-powered sustainability transformation story** for {company_name} in the {industry} industry.
            
            📌 **Strategic Storytelling Using McKinsey Frameworks**  
            - **Horizon Model**: Short-term & long-term sustainability roadmap  
            - **7-S Framework**: Align strategy, structure, and shared values  
            - **Business Flywheel**: Monetization model similar to Amazon, Netflix, or LinkedIn  
            - **CSRD Compliance**: Map sustainability impact to financial metrics  

            🎯 **Key Insights & Monetization Strategy**  
            - What sustainability initiatives {company_name} should prioritize?  
            - How can they **monetize sustainability data**?  
            - What investment pathways (venture capital, grants, debt) should they pursue?  
            
            Format the response as a JSON object with these keys:
            {{
              "Company": "{company_name}",
              "Industry": "{industry}",
              "Sustainability Strategy": "...",
              "Monetization Model": "...",
              "Investment Pathway": "...",
              "Actionable Recommendations": ["...", "...", "..."]
            }}
            """

            llm = ChatOpenAI(model="gpt-4-turbo", temperature=0.4)
            response = RetrievalQA.from_chain_type(llm, chain_type="stuff").run(prompt)
            
            # Try to parse the response as JSON
            try:
                if isinstance(response, str):
                    return json.loads(response)
                return response
            except json.JSONDecodeError:
                logger.warning("Failed to parse AI response as JSON, returning raw response")
                return {
                    "Company": company_name,
                    "Industry": industry,
                    "Sustainability Strategy": response,
                    "Monetization Model": "Could not generate",
                    "Investment Pathway": "Could not generate",
                    "Actionable Recommendations": ["Please try again with more specific information"]
                }
                
        except Exception as e:
            logger.error(f"Error using LangChain/OpenAI for storytelling: {str(e)}")
            return generate_mock_sustainability_story(company_name, industry)
    else:
        logger.warning("OpenAI API key not available or LangChain not installed. Using mock storytelling.")
        return generate_mock_sustainability_story(company_name, industry)

def generate_mock_sustainability_story(company_name, industry):
    """
    Generate a mock sustainability story when OpenAI is not available
    
    Args:
        company_name (str): Name of the company
        industry (str): Industry the company operates in
        
    Returns:
        dict: Mock sustainability story
    """
    logger.info(f"Generating mock sustainability story for {company_name}")
    
    # Industry-specific strategy templates
    industry_strategies = {
        "technology": f"{company_name} will focus on reducing e-waste, improving energy efficiency in data centers, and developing sustainable software engineering practices.",
        "manufacturing": f"{company_name} will implement circular economy principles in production, reduce emissions through process optimization, and invest in renewable energy for facilities.",
        "retail": f"{company_name} will create sustainable supply chains, reduce packaging waste, and implement green store designs with energy-efficient operations.",
        "energy": f"{company_name} will accelerate transition to renewable energy sources, implement carbon capture technologies, and optimize grid efficiency.",
        "healthcare": f"{company_name} will reduce medical waste, implement green facility management, and develop sustainable healthcare delivery models.",
        "finance": f"{company_name} will develop ESG investment products, implement sustainable lending practices, and reduce operational carbon footprint.",
        "transportation": f"{company_name} will electrify fleet vehicles, optimize logistics for emissions reduction, and develop sustainable mobility solutions.",
    }
    
    # Default strategy for industries not in our templates
    default_strategy = f"{company_name} will implement a comprehensive sustainability program focusing on emissions reduction, resource efficiency, and stakeholder engagement."
    
    # Get the appropriate strategy based on industry
    strategy = industry_strategies.get(industry.lower(), default_strategy)
    
    # Generate monetization models
    monetization_models = [
        f"Sustainability Data Analytics Platform: {company_name} can monetize its sustainability data by creating an analytics platform that provides benchmarking, insights, and reporting capabilities for other companies in the {industry} industry.",
        f"Sustainability Consulting Services: {company_name} can leverage its expertise to offer consulting services to other organizations looking to improve their sustainability performance.",
        f"Carbon Offset Marketplace: {company_name} can develop a marketplace connecting carbon offset projects with businesses seeking to achieve carbon neutrality.",
        f"Sustainability-as-a-Service (SaaS): {company_name} can offer subscription-based services for ongoing sustainability management, reporting, and optimization.",
        f"Green Product Certification: {company_name} can develop a certification program for sustainable products in the {industry} sector, generating revenue through certification fees."
    ]
    
    # Generate investment pathways
    investment_pathways = [
        f"Green Bonds: {company_name} should issue green bonds to finance specific climate and environmental projects, accessing the growing sustainable debt market.",
        f"Sustainability-Linked Loans: {company_name} can negotiate loans with interest rates tied to achieving sustainability performance targets.",
        f"Venture Capital for Green Innovation: {company_name} should seek venture capital funding for developing innovative sustainable technologies and solutions.",
        f"Government Grants: {company_name} should pursue government grants and incentives for renewable energy adoption and emissions reduction projects.",
        f"Strategic Partnerships: {company_name} should form strategic partnerships with sustainability-focused investors and organizations for joint ventures."
    ]
    
    # Generate recommendations
    recommendations = [
        f"Implement science-based targets for emissions reduction aligned with a 1.5°C pathway",
        f"Develop a comprehensive ESG data management system to improve reporting accuracy and efficiency",
        f"Conduct a full supply chain sustainability assessment to identify hotspots and opportunities",
        f"Invest in renewable energy through on-site generation and power purchase agreements",
        f"Train employees on sustainability principles and integrate into performance metrics",
        f"Engage with industry associations to develop sector-specific sustainability standards",
        f"Launch a product innovation initiative focused on circular economy principles",
        f"Implement water conservation technologies across operations"
    ]
    
    # Create the mock story
    story = {
        "Company": company_name,
        "Industry": industry,
        "Sustainability Strategy": strategy,
        "Monetization Model": random.choice(monetization_models),
        "Investment Pathway": random.choice(investment_pathways),
        "Actionable Recommendations": random.sample(recommendations, 3)
    }
    
    return story
