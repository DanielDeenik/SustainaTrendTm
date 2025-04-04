"""
Simplified FastAPI backend with direct PostgreSQL connection
for the Sustainability Intelligence Platform
"""
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime
import os
import traceback
import psycopg2
from psycopg2.extras import RealDictCursor

# Initialize FastAPI app
app = FastAPI(
    title="Sustainability Metrics API",
    description="API for managing sustainability metrics",
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

# Direct database connection function
def get_db_connection():
    """Get a direct database connection"""
    # Check if DATABASE_URL exists first
    if os.getenv('DATABASE_URL'):
        conn = psycopg2.connect(os.getenv('DATABASE_URL'), cursor_factory=RealDictCursor)
    # Otherwise use individual connection parameters
    elif os.getenv('PGDATABASE') and os.getenv('PGUSER') and os.getenv('PGPASSWORD') and os.getenv('PGHOST'):
        conn = psycopg2.connect(
            dbname=os.getenv('PGDATABASE'),
            user=os.getenv('PGUSER'),
            password=os.getenv('PGPASSWORD'),
            host=os.getenv('PGHOST'),
            port=os.getenv('PGPORT', '5432'),
            cursor_factory=RealDictCursor
        )
    else:
        raise EnvironmentError("Missing required database environment variables")

    return conn

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT 1")
        conn.close()

        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": f"error: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }

@app.get("/api/metrics")
async def get_metrics():
    """Get all metrics with direct database connection"""
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, name, category, value, unit, timestamp
                FROM metrics 
                ORDER BY timestamp DESC
            """)
            rows = cur.fetchall()

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
                    print(f"Error processing row: {row}, error: {str(row_error)}")
                    continue

            conn.close()
            return metrics
    except Exception as e:
        error_traceback = traceback.format_exc()
        print(f"Failed to fetch metrics: {str(e)}")
        print(f"Traceback: {error_traceback}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch metrics: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    print("Starting FastAPI server...")
    uvicorn.run(
        "direct_main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
