from typing import Optional, Literal
from pydantic import BaseModel, Field

PlannerType = Literal["home", "party", "jewelry"]

class RecommendationRequest(BaseModel):
    planner: PlannerType
    budget: float = Field(gt=0, le=100000000)
    currency: str = Field(default="INR", max_length=3)
    preferences: str = Field(default="", max_length=2000)
    location: str = Field(default="India", max_length=120)
    details: dict = Field(default_factory=dict)
