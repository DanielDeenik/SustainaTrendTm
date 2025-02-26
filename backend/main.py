from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime
import os

from backend.database import get_db, verify_db_connection, init_db
from backend.utils.logger import logger
from backend.middleware.error_handler import handle_error

# Initialize FastAPI app
app = FastAPI(
    title="Sustainability Metrics API",
    description="API for managing sustainability metrics",
    version="1.0.0"
)

# Add error handler
app.add_exception_handler(Exception, handle_error)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        if verify_db_connection():
            return {
                "status": "healthy",
                "database": "connected",
                "timestamp": datetime.now().isoformat()
            }
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Health check failed"
        )

@app.get("/api/metrics")
async def get_metrics():
    """Get all metrics with improved error handling"""
    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT id, name, category, value, unit, timestamp
                    FROM metrics 
                    ORDER BY timestamp DESC
                """)
                rows = cur.fetchall()

                metrics = []
                for row in rows:
                    metric_dict = dict(row)
                    metrics.append({
                        "id": metric_dict['id'],
                        "name": metric_dict['name'],
                        "category": metric_dict['category'],
                        "value": float(metric_dict['value']),
                        "unit": metric_dict['unit'],
                        "timestamp": metric_dict['timestamp'].isoformat()
                    })

                logger.info(f"Successfully fetched {len(metrics)} metrics")
                return metrics
    except Exception as e:
        logger.error(f"Failed to fetch metrics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch metrics"
        )

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    try:
        # Initialize database and create tables
        init_db()
        logger.info("Successfully initialized database")
    except Exception as e:
        logger.error(f"Startup error: {str(e)}")
        raise

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting FastAPI server...")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )