#!/bin/bash
# Install Python dependencies if needed
pip install fastapi uvicorn psycopg2-binary pydantic python-dotenv sqlalchemy

# Start the FastAPI server
python3 main.py