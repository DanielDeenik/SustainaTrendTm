#!/bin/bash
# Install Python dependencies if needed
pip install fastapi uvicorn psycopg2-binary pydantic python-dotenv sqlalchemy

# Start the FastAPI server
uvicorn main:app --host 0.0.0.0 --port 8000 --reload