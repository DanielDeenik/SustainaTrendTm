#!/usr/bin/env python3
"""
Test script for DocumentProcessor field extraction
"""
import os
from frontend.document_processor import DocumentProcessor

def main():
    """
    Test the DocumentProcessor's ability to extract structured fields from documents
    """
    # Create test document text
    test_document = """
    Investment Thesis 2024
    Green Future Capital Partners
    
    Investment Focus: Clean Energy
    Fund Stage: Series A
    
    Focus Areas:
    Our fund focuses on revolutionary clean energy technologies 
    that can disrupt the traditional energy sector while reducing
    carbon emissions and promoting sustainability.
    
    Analysis Requirements:
    We seek to evaluate companies against rigorous ESG standards
    and assess their potential to deliver both financial returns
    and meaningful climate impact.
    """
    
    # Initialize document processor
    processor = DocumentProcessor()
    
    # Test field extraction
    print("Testing field extraction for investment thesis...")
    
    result = processor.extract_structured_fields(test_document, "investment_thesis")
    
    # Print results
    print("\nExtraction Result:")
    print(f"Success: {result['success']}")
    print(f"Method: {result.get('method', 'AI')}")
    print(f"Confidence: {result.get('confidence', 'Unknown')}")
    
    print("\nExtracted Fields:")
    for field, value in result['fields'].items():
        print(f"  {field}: {value}")

if __name__ == "__main__":
    main()