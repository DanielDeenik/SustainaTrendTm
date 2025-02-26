#!/usr/bin/env python3
"""
Standalone script to run the FastAPI backend
"""
import os
import sys
import uvicorn

def run_fastapi():
    """Run the FastAPI backend directly"""
    print("Starting FastAPI backend...")
    
    # Set the Python path to include the backend directory
    backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend")
    sys.path.insert(0, backend_dir)
    
    # Change to the backend directory
    os.chdir(backend_dir)
    
    # Print environment variables for debugging (without values)
    print("\nEnvironment variables:")
    print(f"DATABASE_URL exists: {bool(os.getenv('DATABASE_URL'))}")
    print(f"PGDATABASE exists: {bool(os.getenv('PGDATABASE'))}")
    print(f"PGUSER exists: {bool(os.getenv('PGUSER'))}")
    print(f"PGHOST exists: {bool(os.getenv('PGHOST'))}")
    print(f"PGPORT exists: {bool(os.getenv('PGPORT'))}")
    
    # Run the FastAPI application
    print("\nStarting FastAPI server on port 8000...")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, log_level="info")

if __name__ == "__main__":
    run_fastapi()
