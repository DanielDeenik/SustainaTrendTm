from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime
import os
import traceback

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
        logger.info("Health check endpoint called")
        db_status = verify_db_connection()
        db_status_message = "connected" if db_status else "disconnected"
        logger.info(f"Database status: {db_status_message}")

        response = {
            "status": "healthy" if db_status else "unhealthy",
            "database": db_status_message,
            "timestamp": datetime.now().isoformat()
        }

        logger.info(f"Health check response: {response}")
        return response
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
        logger.info("API metrics endpoint called")
        with get_db() as conn:
            with conn.cursor() as cur:
                logger.info("Executing SQL query to fetch metrics")
                cur.execute("""
                    SELECT id, name, category, value, unit, timestamp
                    FROM metrics 
                    ORDER BY timestamp DESC
                """)
                rows = cur.fetchall()
                logger.info(f"Query returned {len(rows)} rows")

                metrics = []
                for row in rows:
                    try:
                        metric_dict = dict(row)
                        metrics.append({
                            "id": metric_dict['id'],
                            "name": metric_dict['name'],
                            "category": metric_dict['category'],
                            "value": float(metric_dict['value']),
                            "unit": metric_dict['unit'],
                            "timestamp": metric_dict['timestamp'].isoformat()
                        })
                    except Exception as row_error:
                        logger.error(f"Error processing row: {row}, error: {str(row_error)}")
                        # Continue processing other rows instead of failing
                        continue

                # Log sample of the data for verification
                if metrics and len(metrics) > 0:
                    logger.info(f"Sample metric from database: {metrics[0]}")
                    categories = set(m['category'] for m in metrics)
                    logger.info(f"Metric categories in database: {categories}")

                logger.info(f"Successfully fetched {len(metrics)} metrics")
                return metrics
    except Exception as e:
        error_traceback = traceback.format_exc()
        logger.error(f"Failed to fetch metrics: {str(e)}")
        logger.error(f"Traceback: {error_traceback}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch metrics: {str(e)}"
        )

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    try:
        logger.info("FastAPI application starting up")
        # Initialize database and create tables
        init_db()
        logger.info("Successfully initialized database")

        # Log environment information (without sensitive data)
        logger.info(f"DATABASE_URL exists: {bool(os.getenv('DATABASE_URL'))}")
        logger.info(f"PGDATABASE exists: {bool(os.getenv('PGDATABASE'))}")
        logger.info(f"PGHOST exists: {bool(os.getenv('PGHOST'))}")
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