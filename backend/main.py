from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import logging
from datetime import datetime

from backend.models import Metric, MetricCreate
from backend.database import get_db, verify_db_connection

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Sustainability Metrics API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint for health check"""
    return {"status": "ok", "message": "Sustainability Metrics API is running"}

@app.get("/api/metrics", response_model=List[Metric])
async def get_metrics():
    """Get all metrics"""
    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM metrics ORDER BY timestamp DESC")
                rows = cur.fetchall()
                metrics = [
                    Metric(
                        id=row[0],
                        name=row[1],
                        category=row[2],
                        value=float(row[3]),
                        unit=row[4],
                        timestamp=row[5]
                    )
                    for row in rows
                ]
                return metrics
    except Exception as e:
        logger.error(f"Error fetching metrics: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={"message": "Failed to fetch metrics", "error": str(e)}
        )

@app.post("/api/metrics", response_model=Metric, status_code=201)
async def create_metric(metric: MetricCreate):
    """Create a new metric"""
    try:
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO metrics (name, category, value, unit)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id, name, category, value, unit, timestamp
                    """,
                    (metric.name, metric.category, metric.value, metric.unit)
                )
                row = cur.fetchone()
                return Metric(
                    id=row[0],
                    name=row[1],
                    category=row[2],
                    value=float(row[3]),
                    unit=row[4],
                    timestamp=row[5]
                )
    except Exception as e:
        logger.error(f"Error creating metric: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={"message": "Failed to create metric", "error": str(e)}
        )

@app.on_event("startup")
async def startup_event():
    """Verify database connection on startup"""
    if not verify_db_connection():
        logger.error("Failed to connect to database")
        raise Exception("Database connection failed")
    logger.info("Successfully connected to database")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)