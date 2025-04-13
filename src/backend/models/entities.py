from datetime import datetime
from typing import Dict, List, Optional, Union
from pydantic import BaseModel, Field
from bson import ObjectId

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")

class VC(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    name: str
    description: str
    founded_year: int
    headquarters: str
    website: str
    total_funds_raised: float
    active_funds: List[PyObjectId] = []
    portfolio_companies: List[PyObjectId] = []
    investment_thesis: str
    sustainability_focus: List[str]
    key_metrics: Dict[str, float]
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class Fund(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    name: str
    vc_id: PyObjectId
    size: float
    vintage_year: int
    status: str  # active, closed, raising
    investment_strategy: str
    target_sectors: List[str]
    sustainability_criteria: Dict[str, Union[str, List[str]]]
    portfolio_companies: List[PyObjectId] = []
    performance_metrics: Dict[str, float]
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class Company(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    name: str
    description: str
    founded_year: int
    headquarters: str
    website: str
    sector: str
    sub_sectors: List[str]
    funding_rounds: List[Dict[str, Union[str, float, datetime]]]
    investors: List[PyObjectId]
    sustainability_metrics: Dict[str, float]
    esg_ratings: Dict[str, str]
    growth_metrics: Dict[str, float]
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class Trend(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    name: str
    description: str
    category: str
    sub_categories: List[str]
    relevance_score: float
    growth_rate: float
    maturity_stage: str  # emerging, growing, mature, declining
    related_companies: List[PyObjectId]
    related_vcs: List[PyObjectId]
    market_size: float
    key_metrics: Dict[str, float]
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str} 