"""
Test script for VC Benchmark Service

This script demonstrates how to use the VC Benchmark Service to store and analyze
web search sustainability data for venture capital partners.
"""

import os
import sys
import json
from datetime import datetime

# Add the parent directory to the path so we can import the service
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.vc_benchmark_service import VCBenchmarkService

def main():
    """Main function to test VC Benchmark Service"""
    print("Testing VC Benchmark Service...")
    
    # Initialize the service
    service = VCBenchmarkService()
    
    # Sample VC partner data
    partner_data = {
        "name": "GreenTech Ventures",
        "description": "A venture capital firm focused on sustainable technology investments",
        "founded_year": 2015,
        "headquarters": "San Francisco, CA",
        "aum": "500M",  # Assets under management
        "portfolio_size": 25,
        "sustainability_focus": "High",
        "website": "https://example.com/greentech-ventures"
    }
    
    # Add the VC partner
    print("\nAdding VC partner...")
    result = service.add_vc_partner(partner_data)
    
    if result["success"]:
        partner_id = result["partner_id"]
        print(f"Successfully added VC partner with ID: {partner_id}")
    else:
        print(f"Failed to add VC partner: {result.get('error', 'Unknown error')}")
        return
    
    # Sample web search data
    search_query = "GreenTech Ventures sustainability initiatives"
    search_data = [
        {
            "title": "GreenTech Ventures Launches $100M Climate Tech Fund",
            "text": "GreenTech Ventures has announced a new $100M fund focused on climate technology startups. The fund will invest in early-stage companies developing solutions for carbon reduction, renewable energy, and sustainable materials.",
            "source": "TechCrunch",
            "url": "https://example.com/news/1",
            "date": "2023-06-15"
        },
        {
            "title": "GreenTech Ventures Portfolio Company Achieves Carbon Neutrality",
            "text": "SolarTech, a portfolio company of GreenTech Ventures, has achieved carbon neutrality across its operations. The company credits this achievement to its innovative solar panel technology and commitment to sustainable practices.",
            "source": "Green Business Journal",
            "url": "https://example.com/news/2",
            "date": "2023-08-22"
        },
        {
            "title": "GreenTech Ventures Publishes First Sustainability Report",
            "text": "GreenTech Ventures has published its first sustainability report, detailing its approach to ESG investing and the impact of its portfolio companies. The report highlights a 30% reduction in carbon emissions across the portfolio since 2020.",
            "source": "Venture Capital Weekly",
            "url": "https://example.com/news/3",
            "date": "2023-10-05"
        }
    ]
    
    # Store the web search data
    print("\nStoring web search data...")
    result = service.store_web_search_data(
        partner_name=partner_data["name"],
        search_query=search_query,
        data=search_data
    )
    
    if result["success"]:
        search_id = result["search_id"]
        print(f"Successfully stored web search data with ID: {search_id}")
        print(f"Items stored: {result['items_stored']}")
    else:
        print(f"Failed to store web search data: {result.get('error', 'Unknown error')}")
    
    # Create a benchmark
    print("\nCreating benchmark...")
    benchmark_criteria = {
        "carbon_reduction": 0.3,
        "renewable_energy": 0.2,
        "sustainable_materials": 0.2,
        "water_conservation": 0.15,
        "waste_reduction": 0.15
    }
    
    result = service.create_benchmark(
        benchmark_name="Climate Tech VC Benchmark",
        criteria=benchmark_criteria,
        description="Benchmark for evaluating VC firms' sustainability initiatives"
    )
    
    if result["success"]:
        benchmark_id = result["benchmark_id"]
        print(f"Successfully created benchmark with ID: {benchmark_id}")
    else:
        print(f"Failed to create benchmark: {result.get('error', 'Unknown error')}")
        return
    
    # Evaluate the partner against the benchmark
    print("\nEvaluating partner against benchmark...")
    result = service.evaluate_partner_against_benchmark(partner_id, benchmark_id)
    
    if result["success"]:
        evaluation = result["evaluation"]
        print(f"Evaluation completed for {evaluation['partner_name']} against {evaluation['benchmark_name']}")
        print(f"Overall score: {evaluation['overall_score']:.2f}")
        
        print("\nCriteria scores:")
        for criterion, score in evaluation["criteria_scores"].items():
            print(f"  - {criterion}: {score:.2f}")
        
        print("\nRecommendations:")
        for i, recommendation in enumerate(evaluation["recommendations"], 1):
            print(f"  {i}. {recommendation}")
    else:
        print(f"Failed to evaluate partner: {result.get('error', 'Unknown error')}")
    
    # Retrieve sustainability data
    print("\nRetrieving sustainability data...")
    result = service.get_sustainability_data(partner_name=partner_data["name"])
    
    if result["success"]:
        data = result["data"]
        print(f"Retrieved {result['count']} sustainability data items")
        
        if data:
            print("\nSample data:")
            for i, item in enumerate(data[:2], 1):
                print(f"\nItem {i}:")
                print(f"  Search ID: {item['search_id']}")
                print(f"  Query: {item['search_query']}")
                print(f"  Created: {item['created_at']}")
                print(f"  Data items: {len(item['data'])}")
    else:
        print(f"Failed to retrieve sustainability data: {result.get('error', 'Unknown error')}")
    
    print("\nTest completed!")

if __name__ == "__main__":
    main() 