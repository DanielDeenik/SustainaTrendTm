from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from backend.database import get_db
from backend.models import MetricModel, MetricCreate, Metric
from backend.utils.logger import logger

router = APIRouter()

@router.get("/metrics", response_model=List[Metric])
async def get_metrics(category: str = None, db: Session = Depends(get_db)):
    try:
        logger.info(
            "Fetching metrics",
            extra={
                "category": category
            }
        )
        query = db.query(MetricModel)
        if category:
            query = query.filter(MetricModel.category == category)
        return query.all()
    except Exception as e:
        logger.error("Error fetching metrics", extra={"error": str(e)})
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/metrics", response_model=Metric, status_code=201)
async def create_metric(metric: MetricCreate, db: Session = Depends(get_db)):
    try:
        logger.info(
            "Creating new metric",
            extra={
                "metric_data": metric.dict()
            }
        )
        db_metric = MetricModel(**metric.dict())
        db.add(db_metric)
        db.commit()
        db.refresh(db_metric)
        return db_metric
    except Exception as e:
        logger.error("Error creating metric", extra={"error": str(e)})
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")
