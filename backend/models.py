from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from pydantic.functional_validators import field_validator
from sqlalchemy import Column, Integer, String, DateTime, JSON, Text, Numeric, text
from sqlalchemy.ext.declarative import declarative_base
import json
import logging
from enum import Enum

from backend.database import Base
from backend.utils.logger import logger

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
    name = Column(Text, nullable=False)
    category = Column(Text, nullable=False)
    value = Column(Numeric(precision=18, scale=6), nullable=False)
    unit = Column(Text, nullable=False)
    timestamp = Column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    metric_metadata = Column(JSON, nullable=True, server_default=text("'{}'::jsonb"))

    def __repr__(self):
        return f"<Metric(id={self.id}, name='{self.name}', category='{self.category}')>"

    def to_dict(self) -> Dict[str, Any]:
        try:
            return {
                "id": self.id,
                "name": self.name,
                "category": self.category,
                "value": float(self.value) if self.value is not None else 0.0,
                "unit": self.unit,
                "timestamp": self.timestamp.isoformat() if self.timestamp else datetime.utcnow().isoformat(),
                "metric_metadata": self.metric_metadata if self.metric_metadata else {}
            }
        except Exception as e:
            logger.error(
                "Error converting metric to dict",
                extra={
                    "error": str(e),
                    "metric_id": self.id,
                    "metric_name": self.name,
                    "metric_category": self.category,
                    "metric_value": str(self.value) if self.value is not None else None,
                    "metric_unit": self.unit,
                    "metric_timestamp": str(self.timestamp) if self.timestamp else None,
                    "metric_metadata": str(self.metric_metadata) if self.metric_metadata else None
                },
                exc_info=True
            )
            raise

# Pydantic models for request/response validation
class MetricBase(BaseModel):
    name: str = Field(..., min_length=1, description="Name of the metric")
    category: MetricCategory = Field(..., description="Category of the metric")
    value: float = Field(..., ge=0, description="Value of the metric")
    unit: str = Field(..., min_length=1, description="Unit of measurement")
    metric_metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "name": "Carbon Footprint",
                "category": "emissions",
                "value": 100.5,
                "unit": "kg CO2e",
                "metric_metadata": {"source": "direct measurement", "location": "Factory A"}
            }
        }
    )

    @field_validator('metric_metadata', mode='before')
    @classmethod
    def ensure_dict(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                raise ValueError('Invalid JSON format for metric_metadata')
        return v or {}

class MetricCreate(MetricBase):
    pass

class Metric(MetricBase):
    id: int
    timestamp: datetime

    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            datetime: lambda v: v.isoformat(),
        }
    )

class EnvironmentalMetrics(BaseModel):
    carbon_emissions: float = Field(ge=0)
    energy_usage: float = Field(ge=0)
    waste_generation: float = Field(ge=0)
    water_consumption: float = Field(ge=0)
    renewable_energy_percentage: float = Field(ge=0, le=100)
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)

class SocialMetrics(BaseModel):
    employee_count: int = Field(ge=0)
    diversity_score: float = Field(ge=0, le=100)
    community_investment: float = Field(ge=0)
    employee_satisfaction: float = Field(ge=0, le=100)
    health_and_safety_incidents: int = Field(ge=0)
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)

class GovernanceMetrics(BaseModel):
    board_diversity: float = Field(ge=0, le=100)
    ethics_violations: int = Field(ge=0)
    policy_compliance: float = Field(ge=0, le=100)
    transparency_score: float = Field(ge=0, le=100)
    risk_management_score: float = Field(ge=0, le=100)
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)

class SustainabilityMetrics(BaseModel):
    id: Optional[str] = None
    company_id: str
    environmental: EnvironmentalMetrics
    social: SocialMetrics
    governance: GovernanceMetrics
    overall_score: float = Field(ge=0, le=100)
    last_updated: datetime

    model_config = ConfigDict(from_attributes=True)