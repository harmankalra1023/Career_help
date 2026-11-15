from typing import Dict, Any, List, Optional
from pydantic import BaseModel


class ScoreDetailSchema(BaseModel):
    value: float
    band: str
    confidence: float
    delta_since_last: Optional[float] = None
    as_of: str


class ScoresOverview(BaseModel):
    profile: ScoreDetailSchema
    technical: ScoreDetailSchema
    non_technical: ScoreDetailSchema
    career_match_top: Optional[Dict[str, Any]] = None
    industry_demand: Optional[Dict[str, Any]] = None
    job_readiness: Optional[Dict[str, Any]] = None


class DashboardResponse(BaseModel):
    scores: ScoresOverview
    dna: Dict[str, Any]
    strengths: List[Dict[str, Any]]
    gaps: List[Dict[str, Any]]
    target_roles: List[Dict[str, Any]]
    data_quality: Dict[str, Any]
