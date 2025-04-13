from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from datetime import datetime

from backend.database import get_db
from backend.models import MetricModel, MetricCreate, Metric
from backend.utils.logger import logger

router = APIRouter()

@router.get("/metrics", response_model=List[Metric])
async def get_metrics(
    category: Optional[str] = None,
):
    """
    Get all metrics or filter by category
    """
    try:
        logger.info(
            "Fetching metrics",
            extra={
                "category": category
            }
        )
        metrics = []

        with get_db() as db:
            query = db.query(MetricModel)
            if category:
                query = query.filter(MetricModel.category == category)

            db_metrics = query.all()

            for db_metric in db_metrics:
                try:
                    metric_dict = db_metric.to_dict()
                    metric = Metric(**metric_dict)
                    metrics.append(metric)
                except Exception as conversion_error:
                    logger.error(
                        "Error converting metric",
                        extra={
                            "metric_id": db_metric.id,
                            "error": str(conversion_error)
                        },
                        exc_info=True
                    )
                    # Continue processing other metrics
                    continue

        return metrics
    except Exception as e:
        logger.error(
            "Error fetching metrics",
            extra={
                "error": str(e),
                "category": category
            },
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch metrics: {str(e)}"
        )

@router.post("/metrics", response_model=Metric, status_code=status.HTTP_201_CREATED)
async def create_metric(
    metric: MetricCreate,
):
    """
    Create a new metric
    """
    try:
        logger.info(
            "Creating new metric",
            extra={
                "metric_data": metric.model_dump()
            }
        )

        with get_db() as db:
            db_metric = MetricModel(
                name=metric.name,
                category=metric.category,
                value=metric.value,
                unit=metric.unit,
                metric_metadata=metric.metric_metadata or {}
            )

            db.add(db_metric)
            db.commit()
            db.refresh(db_metric)

            metric_dict = db_metric.to_dict()
            return Metric(**metric_dict)
    except Exception as e:
        logger.error(
            "Error creating metric",
            extra={
                "error": str(e),
                "metric_data": metric.model_dump()
            },
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create metric: {str(e)}"
        )