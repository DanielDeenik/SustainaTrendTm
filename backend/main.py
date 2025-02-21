import os
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import logging
import sys
from typing import List, Optional
from sqlalchemy.orm import Session

from models import MetricModel, MetricCreate, Metric
from database import get_db, init_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Sustainability Intelligence API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database tables
init_db()
logger.info("Database tables initialized")

@app.get("/")
async def read_root():
    return {"message": "Welcome to Sustainability Intelligence API"}

@app.get("/api/metrics", response_model=List[Metric])
async def get_metrics(
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    try:
        query = db.query(MetricModel)
        if category:
            query = query.filter(MetricModel.category == category)
        metrics = query.order_by(MetricModel.timestamp.desc()).all()
        return metrics
    except Exception as e:
        logger.error(f"Error fetching metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/metrics", response_model=Metric)
async def create_metric(
    metric: MetricCreate,
    db: Session = Depends(get_db)
):
    try:
        metric_data = metric.model_dump()  # Using model_dump instead of deprecated dict()
        logger.info(f"Processing metric data: {metric_data}")

        db_metric = MetricModel(**metric_data)
        logger.info(f"Created MetricModel instance")

        db.add(db_metric)
        db.commit()
        db.refresh(db_metric)

        return db_metric
    except Exception as e:
        logger.error(f"Error creating metric: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)