from typing import List, Optional, Dict, Any
from pydantic import BaseModel


class RoadmapCreateRequest(BaseModel):
    target_role: str
    horizon_months: int = 6
    weekly_hours: float = 8.0
    budget: Dict[str, Any] = {"currency": "USD", "max_total": 0}
    prefer_free: bool = True


class MilestoneResponse(BaseModel):
    id: str
    sequence_order: int
    title: str
    phase: str
    month_index: int
    estimated_hours: float
    is_locked: bool
    status: str
    skills: List[str]
    resources: List[Dict[str, Any]]


class RoadmapResponse(BaseModel):
    id: str
    target_role_slug: str
    horizon_months: int
    weekly_hours: float
    milestones: List[MilestoneResponse]
