#!/usr/bin/env python3
"""
Standalone runner for FastAPI backend
"""
import uvicorn
import os
import sys

def run_fastapi():
    """Run the FastAPI backend without timeout"""
    print("Starting FastAPI backend...")
    
    # Print environment variables for debugging (without showing sensitive values)
    print("Database configuration:")
    print(f"DATABASE_URL exists: {bool(os.getenv('DATABASE_URL'))}")
    print(f"PGDATABASE exists: {bool(os.getenv('PGDATABASE'))}")
    print(f"PGUSER exists: {bool(os.getenv('PGUSER'))}")
    print(f"PGHOST exists: {bool(os.getenv('PGHOST'))}")
    print(f"PGPORT exists: {bool(os.getenv('PGPORT'))}")
    
    # Run FastAPI with the simplified main file that has direct PostgreSQL connection
    uvicorn.run(
        "direct_main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    run_fastapi()
