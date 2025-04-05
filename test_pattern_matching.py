#!/usr/bin/env python3
"""
Test script for pattern matching functionality in DocumentProcessor
"""
import os
import sys
from frontend.document_processor import DocumentProcessor

def main():
    """
    Test the DocumentProcessor's pattern matching capabilities
    """
    # Create test document texts with various formats
    test_docs = {
        "investment_thesis_1": """
        INVESTMENT THESIS 2024
        Green Future Capital Partners
        Fund Name: Green Future Climate Fund
        
        Investment Focus: Clean Energy
        Fund Stage: Series A
        Year: 2024
        
        Focus Areas:
        Our fund focuses on revolutionary clean energy technologies 
        that can disrupt the traditional energy sector while reducing
        carbon emissions and promoting sustainability.
        
        Analysis Requirements:
        We seek to evaluate companies against rigorous ESG standards
        and assess their potential to deliver both financial returns
        and meaningful climate impact.
        """,
        
        "investment_thesis_2": """
        Climate Tech Fund IV
        Sustainable Ventures
        
        2025 Investment Thesis
        
        Our investment focuses on early-stage climate tech innovations
        with particular emphasis on energy storage and grid solutions.
        
        Fund primarily targets Series A companies with proven technology
        and early market traction.
        
        Analysis Objectives:
        - Evaluate climate impact potential
        - Assess market scalability
        - Verify technology readiness
        - Analyze team capabilities
        """,
        
        "startup_assessment_1": """
        COMPANY PROFILE
        
        Company name: EcoSolutions Inc.
        Industry: Clean Technology
        Founded: 2018
        Funding Stage: Seed
        
        Sustainability Vision:
        EcoSolutions aims to revolutionize waste management through
        AI-powered sorting and recycling technologies that significantly
        reduce landfill waste while creating valuable recycled materials.
        
        Current Practices:
        - Carbon-neutral operations
        - 100% renewable energy powered facilities
        - Zero-waste manufacturing process
        
        Challenges:
        - Scaling technology to industrial volumes
        - Regulatory approvals in multiple jurisdictions
        - Establishing reliable supply chains
        
        Metrics Tracked:
        - Tons of waste diverted from landfills
        - CO2 emissions avoided
        - Energy efficiency ratio
        - Material recovery rates
        
        Competitive Advantage:
        Our proprietary AI algorithms achieve 95% sorting accuracy,
        significantly higher than industry standards of 70-80%.
        
        Investor Alignment:
        Our mission directly supports UN SDGs 7, 11, 12, and 13,
        aligning with impact investors focused on waste reduction,
        circular economy, and climate action.
        """,
        
        "startup_assessment_2": """
        AquaTech Solutions
        A Water Conservation Technology Company
        Company Name: AquaTech Solutions Inc.
        
        Sector: Water Technology
        Est. 2020
        Current funding: Pre-seed
        
        MISSION & VISION
        Our sustainability vision is to preserve global freshwater
        resources through smart monitoring and conservation technologies
        that enable industrial and agricultural users to reduce water
        consumption by up to 40%.
        
        SUSTAINABILITY VISION: To transform water management through AI and IoT-powered solutions
        that dramatically reduce water wastage in industrial and agricultural sectors.
        
        We currently implement IoT sensor networks for real-time
        water quality and usage monitoring, use AI to predict
        maintenance needs, and develop closed-loop water recycling systems.
        
        SUSTAINABILITY METRICS TRACKING:
        * Gallons of water saved
        * Reduction in contamination levels
        * System uptime percentage
        * Energy efficiency of water treatment
        
        BUSINESS CHALLENGES include regulatory approval timelines,
        hardware supply chain disruptions, and scaling installation
        capacity to meet demand.
        
        COMPETITIVE ADVANTAGE
        Our technology provides 3x faster leak detection than competitors,
        reducing water waste and associated costs significantly.
        
        INVESTOR INFORMATION
        We align with investors interested in water security, climate
        resilience, and agricultural technology, particularly those
        with portfolios addressing UN SDG 6 (Clean Water and Sanitation).
        """
    }
    
    # Initialize document processor
    processor = DocumentProcessor()
    
    # Test pattern matching for each document type
    for doc_name, doc_text in test_docs.items():
        print(f"\n===== Testing {doc_name} =====")
        
        # Determine form type from document name
        if "investment_thesis" in doc_name:
            form_type = "investment_thesis"
        elif "startup_assessment" in doc_name:
            form_type = "startup_assessment"
        else:
            form_type = "unknown"
        
        # Extract fields using pattern matching
        result = processor._extract_fields_with_patterns(doc_text, form_type)
        
        # Print results
        print(f"Form Type: {form_type}")
        print("Extracted Fields:")
        for field, value in result['fields'].items():
            print(f"  {field}: {value}")
        print()

if __name__ == "__main__":
    main()