#!/usr/bin/env python3
"""
Test Server for SustainaTrend - Minimal Version
"""
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({"status": "running", "message": "SustainaTrend test server is working"})

@app.route('/debug')
def debug():
    return jsonify({"routes": [str(rule) for rule in app.url_map.iter_rules()]})

if __name__ == "__main__":
    print("Starting test server on port 5001")
    app.run(host="0.0.0.0", port=5001, debug=True)