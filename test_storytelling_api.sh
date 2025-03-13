#!/bin/bash

# Test the storytelling API with different audience types and narrative focuses
echo "Testing storytelling API..."

# Board audience with performance analysis focus
echo -e "\n\nTesting Board audience with Performance Analysis focus:"
curl -X POST -H "Content-Type: application/json" -d '{
    "metric": "Carbon Emissions",
    "time_period": "Last Quarter",
    "narrative_focus": "Performance Analysis",
    "audience": "Board",
    "data_source": "metrics"
}' http://localhost:5000/api/storytelling | jq . || echo "Failed to parse JSON"

# Sustainability Team audience with risk assessment focus
echo -e "\n\nTesting Sustainability Team audience with Risk Assessment focus:"
curl -X POST -H "Content-Type: application/json" -d '{
    "metric": "Water Usage",
    "time_period": "Last Year",
    "narrative_focus": "Risk Assessment",
    "audience": "Sustainability Team",
    "data_source": "metrics"
}' http://localhost:5000/api/storytelling | jq . || echo "Failed to parse JSON"

# Investors audience with CSRD/ESG compliance focus
echo -e "\n\nTesting Investors audience with CSRD/ESG Compliance focus:"
curl -X POST -H "Content-Type: application/json" -d '{
    "metric": "Renewable Energy",
    "time_period": "Current Year",
    "narrative_focus": "CSRD/ESG Compliance",
    "audience": "Investors",
    "data_source": "trends"
}' http://localhost:5000/api/storytelling | jq . || echo "Failed to parse JSON"

echo -e "\n\nTesting complete."