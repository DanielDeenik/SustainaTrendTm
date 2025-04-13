"""
Utility script to list all registered routes in the Flask application
"""
import os
import sys

# Add the current directory to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# Import the app
from app import create_app

app = create_app()

# List all routes
print("\nRegistered Routes:")
print("-----------------")
for rule in sorted(app.url_map.iter_rules(), key=lambda x: str(x)):
    print(f"Route: {rule.rule} | Endpoint: {rule.endpoint} | Methods: {', '.join(rule.methods)}")

# Specifically check for regulatory-ai routes
print("\nRegulatory AI Routes:")
print("--------------------")
regulatory_found = False
for rule in sorted(app.url_map.iter_rules(), key=lambda x: str(x)):
    if 'regulatory' in str(rule.rule).lower() or 'regulatory' in str(rule.endpoint).lower():
        regulatory_found = True
        print(f"Route: {rule.rule} | Endpoint: {rule.endpoint} | Methods: {', '.join(rule.methods)}")

if not regulatory_found:
    print("No regulatory routes found!")

# Debug all registered blueprints
print("\nRegistered Blueprints:")
print("--------------------")
for name, blueprint in app.blueprints.items():
    print(f"Blueprint: {name} | URL Prefix: {blueprint.url_prefix}")