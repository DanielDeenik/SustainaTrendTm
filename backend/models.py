from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID

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
