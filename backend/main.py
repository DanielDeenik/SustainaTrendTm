import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import logging
import sys
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Optional
from pydantic import BaseModel

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Sustainability Intelligence API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database connection
def get_db_connection():
    try:
        conn = psycopg2.connect(
            os.environ["DATABASE_URL"],
            cursor_factory=RealDictCursor
        )
        return conn
    except Exception as e:
        logger.error(f"Database connection error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database connection error")

# Pydantic models for request/response
class MetricBase(BaseModel):
    name: str
    category: str
    value: float
    unit: str
    metadata: dict = {}

class MetricCreate(MetricBase):
    pass

class Metric(MetricBase):
    id: int
    timestamp: datetime

@app.get("/")
async def read_root():
    return {"message": "Welcome to Sustainability Intelligence API"}

@app.get("/api/metrics", response_model=List[Metric])
async def get_metrics(category: Optional[str] = None):
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        if category:
            cur.execute(
                "SELECT * FROM metrics WHERE category = %s ORDER BY timestamp DESC",
                (category,)
            )
        else:
            cur.execute("SELECT * FROM metrics ORDER BY timestamp DESC")

        metrics = cur.fetchall()
        cur.close()
        conn.close()
        return metrics
    except Exception as e:
        logger.error(f"Error fetching metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/metrics", response_model=Metric)
async def create_metric(metric: MetricCreate):
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute(
            """
            INSERT INTO metrics (name, category, value, unit, metadata)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id, name, category, value, unit, metadata, timestamp
            """,
            (metric.name, metric.category, metric.value, metric.unit, metric.metadata)
        )

        new_metric = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()

        return new_metric
    except Exception as e:
        logger.error(f"Error creating metric: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)