#!/bin/bash

# Test script for Strategy Hub Consolidation
# This script tests both direct access to the Enhanced Strategy Hub
# and redirects from legacy routes

echo "====== Testing Strategy Hub Consolidation ======"
echo "Testing direct access to Enhanced Strategy Hub..."
curl -s -o /dev/null -w "Enhanced Strategy Hub (direct): %{http_code}\n" http://localhost:5000/enhanced-strategy-hub

echo -e "\nTesting redirects from legacy routes..."
echo "Legacy routes should return 302 status code and redirect to Enhanced Strategy Hub"

# Test main strategy routes
curl -s -o /dev/null -w "Strategy Hub: %{http_code}\n" -I http://localhost:5000/strategy/hub
curl -s -o /dev/null -w "Strategy Framework: %{http_code}\n" -I http://localhost:5000/strategy/framework/esrs
curl -s -o /dev/null -w "Strategy Documents: %{http_code}\n" -I http://localhost:5000/strategy/documents
curl -s -o /dev/null -w "Strategy Modeling Tool: %{http_code}\n" -I http://localhost:5000/strategy/modeling-tool
curl -s -o /dev/null -w "Strategy Test Redirect: %{http_code}\n" -I http://localhost:5000/strategy/test-redirect

echo -e "\nTesting full redirects (following redirect)..."
echo "These should all return 200 OK after following the redirect"

# Test following redirects
curl -s -o /dev/null -w "Strategy Hub (follow redirect): %{http_code}\n" -L http://localhost:5000/strategy/hub
curl -s -o /dev/null -w "Strategy Framework (follow redirect): %{http_code}\n" -L http://localhost:5000/strategy/framework/esrs
curl -s -o /dev/null -w "Strategy Test Redirect (follow redirect): %{http_code}\n" -L http://localhost:5000/strategy/test-redirect

echo -e "\n====== Consolidation Testing Complete ======"