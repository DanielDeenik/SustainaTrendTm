from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime

# Initialize FastAPI app
app = FastAPI(title="Sustainability Metrics API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple database connection function
def get_db_connection():
    """Get a PostgreSQL database connection"""
    try:
        # First try DATABASE_URL if available
        if os.getenv('DATABASE_URL'):
            conn = psycopg2.connect(os.getenv('DATABASE_URL'), cursor_factory=RealDictCursor)
            return conn
        
        # Otherwise use individual parameters
        conn = psycopg2.connect(
            dbname=os.getenv('PGDATABASE'),
            user=os.getenv('PGUSER'),
            password=os.getenv('PGPASSWORD'),
            host=os.getenv('PGHOST'),
            port=os.getenv('PGPORT', '5432'),
            cursor_factory=RealDictCursor
        )
        return conn
    except Exception as e:
        print(f"Database connection error: {str(e)}")
        raise

@app.get("/health")
async def health_check():
    """Simple health check endpoint"""
    try:
        # Test database connection
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT 1")
        conn.close()
        return {"status": "healthy", "database": "connected", "timestamp": datetime.now().isoformat()}
    except Exception as e:
        print(f"Health check failed: {str(e)}")
        return {"status": "unhealthy", "database": f"error: {str(e)}", "timestamp": datetime.now().isoformat()}

@app.get("/api/metrics")
async def get_metrics():
    """Get all sustainability metrics"""
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
        print(f"Failed to fetch metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch metrics: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    print("Starting FastAPI server on port 8000...")
    uvicorn.run("simple_api:app", host="0.0.0.0", port=8000)
