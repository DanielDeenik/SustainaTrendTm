from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from datetime import datetime
import psycopg2
from psycopg2.errors import OperationalError

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
    allow_origins=["http://localhost:3000", "http://0.0.0.0:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
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
                    metric = Metric(
                        id=row['id'],
                        name=row['name'],
                        category=row['category'],
                        value=float(row['value']),
                        unit=row['unit'],
                        timestamp=row['timestamp']
                    )
                    metrics.append(metric)
                return metrics

    except OperationalError as e:
        logger.error("Database connection failed", extra={"error": str(e)})
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "message": "Database is currently unavailable",
                "error": str(e)
            }
        )
    except Exception as e:
        logger.error("Failed to fetch metrics", extra={"error": str(e)})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": "Failed to fetch metrics",
                "error": str(e)
            }
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
                return Metric(
                    id=row['id'],
                    name=row['name'],
                    category=row['category'],
                    value=float(row['value']),
                    unit=row['unit'],
                    timestamp=row['timestamp']
                )
    except psycopg2.IntegrityError as e:
        logger.error("Invalid metric data", extra={"error": str(e)})
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Invalid metric data",
                "error": str(e)
            }
        )
    except Exception as e:
        logger.error("Failed to create metric", extra={"error": str(e)})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": "Failed to create metric",
                "error": str(e)
            }
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)