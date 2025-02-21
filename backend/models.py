from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
import json
import logging
from enum import Enum

logger = logging.getLogger(__name__)

# SQLAlchemy Models
Base = declarative_base()

class MetricCategory(str, Enum):
    EMISSIONS = "emissions"
    WATER = "water"
    ENERGY = "energy"
    WASTE = "waste"
    SOCIAL = "social"
    GOVERNANCE = "governance"

class MetricModel(Base):
    __tablename__ = "metrics"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    value = Column(Float, nullable=False)
    unit = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    metric_metadata = Column(JSON, nullable=True, default={})

    def __repr__(self):
        return f"<Metric(id={self.id}, name='{self.name}', category='{self.category}')>"

    @classmethod
    def create(cls, db, **kwargs):
        try:
            instance = cls(**kwargs)
            db.add(instance)
            db.commit()
            db.refresh(instance)
            return instance
        except Exception as e:
            logger.error(f"Error creating metric: {str(e)}")
            db.rollback()
            raise

# Pydantic models for request/response validation
class MetricBase(BaseModel):
    name: str = Field(..., min_length=1, description="Name of the metric")
    category: MetricCategory = Field(..., description="Category of the metric")
    value: float = Field(..., ge=0, description="Value of the metric")
    unit: str = Field(..., min_length=1, description="Unit of measurement")
    metric_metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    @validator('metric_metadata', pre=True)
    def ensure_dict(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                raise ValueError('Invalid JSON format for metric_metadata')
        return v

    class Config:
        from_attributes = True
        use_enum_values = True

class MetricCreate(MetricBase):
    pass

class Metric(MetricBase):
    id: int
    timestamp: datetime

# Other models remain unchanged
class EnvironmentalMetrics(BaseModel):
    carbon_emissions: float = Field(ge=0)
    energy_usage: float = Field(ge=0)
    waste_generation: float = Field(ge=0)
    water_consumption: float = Field(ge=0)
    renewable_energy_percentage: float = Field(ge=0, le=100)
    timestamp: datetime

class SocialMetrics(BaseModel):
    employee_count: int = Field(ge=0)
    diversity_score: float = Field(ge=0, le=100)
    community_investment: float = Field(ge=0)
    employee_satisfaction: float = Field(ge=0, le=100)
    health_and_safety_incidents: int = Field(ge=0)
    timestamp: datetime

class GovernanceMetrics(BaseModel):
    board_diversity: float = Field(ge=0, le=100)
    ethics_violations: int = Field(ge=0)
    policy_compliance: float = Field(ge=0, le=100)
    transparency_score: float = Field(ge=0, le=100)
    risk_management_score: float = Field(ge=0, le=100)
    timestamp: datetime

class SustainabilityMetrics(BaseModel):
    id: Optional[str] = None
    company_id: str
    environmental: EnvironmentalMetrics
    social: SocialMetrics
    governance: GovernanceMetrics
    overall_score: float = Field(ge=0, le=100)
    last_updated: datetime