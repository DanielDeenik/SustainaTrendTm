from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from enum import Enum

class MetricCategory(str, Enum):
    EMISSIONS = "emissions"
    WATER = "water"
    ENERGY = "energy"
    WASTE = "waste"
    SOCIAL = "social"
    GOVERNANCE = "governance"

class MetricBase(BaseModel):
    name: str = Field(..., description="Name of the metric")
    category: MetricCategory = Field(..., description="Category of the metric")
    value: float = Field(..., ge=0, description="Value of the metric")
    unit: str = Field(..., description="Unit of measurement")

class MetricCreate(MetricBase):
    pass

class Metric(MetricBase):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True