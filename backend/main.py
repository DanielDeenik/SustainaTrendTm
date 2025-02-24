from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import List
from datetime import datetime
import os
from pathlib import Path

from backend.models import Metric, MetricCreate
from backend.database import get_db, verify_db_connection
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

# Add CORS middleware with proper configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api")
async def root():
    """Root endpoint for health check"""
    return {
        "status": "ok",
        "message": "Sustainability Metrics API is running",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/metrics", response_model=List[Metric])
async def get_metrics():
    """Get all metrics with improved error handling"""
    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT id, name, category, value, unit, timestamp, metric_metadata
                    FROM metrics 
                    ORDER BY timestamp DESC
                """)
                rows = cur.fetchall()

                metrics = []
                for row in rows:
                    if row is None:
                        continue
                    try:
                        metric_dict = dict(row)
                        metrics.append(Metric(
                            id=metric_dict['id'],
                            name=metric_dict['name'],
                            category=metric_dict['category'],
                            value=float(metric_dict['value']),
                            unit=metric_dict['unit'],
                            timestamp=metric_dict['timestamp']
                        ))
                    except (KeyError, ValueError) as e:
                        logger.error(f"Error converting row to metric: {e}", extra={"row": row})
                        continue

                return metrics

    except Exception as e:
        logger.error("Failed to fetch metrics", extra={"error": str(e)})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch metrics"
        )

@app.post("/api/metrics", response_model=Metric, status_code=status.HTTP_201_CREATED)
async def create_metric(metric: MetricCreate):
    """Create a new metric with improved error handling"""
    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO metrics (name, category, value, unit)
                    VALUES (%(name)s, %(category)s, %(value)s, %(unit)s)
                    RETURNING id, name, category, value, unit, timestamp
                    """,
                    metric.model_dump()
                )
                row = cur.fetchone()
                if row is None:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Failed to create metric: No data returned"
                    )

                metric_dict = dict(row)
                return Metric(
                    id=metric_dict['id'],
                    name=metric_dict['name'],
                    category=metric_dict['category'],
                    value=float(metric_dict['value']),
                    unit=metric_dict['unit'],
                    timestamp=metric_dict['timestamp']
                )

    except Exception as e:
        logger.error("Failed to create metric", extra={"error": str(e)})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create metric"
        )

@app.on_event("startup")
async def startup_event():
    """Verify database connection on startup"""
    try:
        if not verify_db_connection():
            raise Exception("Database connection failed")
        logger.info("Successfully connected to database")
    except Exception as e:
        logger.error(f"Startup error: {str(e)}")
        raise

# Get the absolute path to the dist directory
static_path = Path(__file__).parent.parent / "dist"

# Create the dist directory if it doesn't exist
static_path.mkdir(parents=True, exist_ok=True)

# Mount the static files directory
app.mount("/", StaticFiles(directory=str(static_path), html=True), name="frontend")

# Fallback route for SPA
@app.get("/{full_path:path}")
async def serve_spa(full_path: str):
    """Serve the SPA index.html for all routes"""
    index_path = static_path / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path))
    raise HTTPException(status_code=404, detail="File not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",  # Bind to all network interfaces
        port=8000,
        reload=True,
        access_log=True
    )