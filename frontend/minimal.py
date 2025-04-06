"""
Minimal Flask application for testing
"""
import os

print("Starting minimal app...")

try:
    from flask import Flask
    print("Flask imported successfully")
except ImportError:
    print("Failed to import Flask")
    exit(1)

app = Flask(__name__)

@app.route('/')
def hello():
    return "Hello World! The app is working."

if __name__ == '__main__':
    print("Running Flask app on port 5000")
    app.run(host='0.0.0.0', port=5000, debug=True)