"""
SustainaTrend Backend Application

This is the main entry point for the SustainaTrend backend application.
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime
import logging
import traceback
import webbrowser
import threading
import time

# Import routers
from routes.sustainability import router as sustainability_router

# Configure logging
from config.logging import get_logger
logger = get_logger("main")

# Initialize FastAPI app
app = FastAPI(
    title="SustainaTrend Platform API",
    description="API for sustainability metrics, analytics, and ethical AI compliance",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(sustainability_router)
logger.info("Included Sustainability routes in FastAPI app")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": f"error: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }

@app.get("/api/metrics")
async def get_metrics():
    """Get all metrics"""
    try:
        # This would be replaced with actual database access
        # For now, return a sample response
        metrics = [
            {
                "id": 1,
                "name": "Carbon Emissions",
                "category": "Environmental",
                "value": 125.5,
                "unit": "tons CO2e",
                "timestamp": datetime.now().isoformat()
            },
            {
                "id": 2,
                "name": "Water Usage",
                "category": "Environmental",
                "value": 450.2,
                "unit": "cubic meters",
                "timestamp": datetime.now().isoformat()
            }
        ]
            return metrics
    except Exception as e:
        error_traceback = traceback.format_exc()
        logger.error(f"Failed to fetch metrics: {str(e)}")
        logger.error(f"Traceback: {error_traceback}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch metrics: {str(e)}"
        )

def open_browser():
    """Open the browser after a short delay to ensure the server is running"""
    time.sleep(2)  # Wait for 2 seconds
    webbrowser.open('http://localhost:8000/docs')

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting FastAPI server...")
    
    # Start the browser in a separate thread
    threading.Thread(target=open_browser, daemon=True).start()
    
    # Start the server
    uvicorn.run(
        "main:app",
        host="127.0.0.1",  # Changed from 0.0.0.0 to 127.0.0.1 for better local access
        port=8000,
        reload=True,
        log_level="info"
    )