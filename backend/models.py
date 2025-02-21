from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base

# SQLAlchemy Models
Base = declarative_base()

class MetricModel(Base):
    __tablename__ = "metrics"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    value = Column(Float, nullable=False)
    unit = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    metric_metadata = Column(JSONB, nullable=True, server_default='{}')

# Pydantic models for request/response validation
class MetricBase(BaseModel):
    name: str
    category: str
    value: float
    unit: str
    metric_metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        from_attributes = True

class MetricCreate(MetricBase):
    pass

class Metric(MetricBase):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

# Domain-specific models for validation
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
    id: Optional[UUID] = None
    company_id: str
    environmental: EnvironmentalMetrics
    social: SocialMetrics
    governance: GovernanceMetrics
    overall_score: float = Field(ge=0, le=100)
    last_updated: datetime