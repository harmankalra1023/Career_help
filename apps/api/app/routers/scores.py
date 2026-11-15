from fastapi import APIRouter, Depends
from app.core.deps import get_current_user_id
from app.schemas.scores import DashboardResponse

router = APIRouter(prefix="/me", tags=["scores"])


@router.get("/dashboard", response_model=DashboardResponse)
async def get_dashboard(user_id: str = Depends(get_current_user_id)):
    return DashboardResponse(
        scores={
            "profile": {
                "value": 64.2,
                "band": "solid",
                "delta_since_last": 3.1,
                "confidence": 0.78,
                "as_of": "2026-11-15",
            },
            "technical": {
                "value": 68.0,
                "band": "solid",
                "delta_since_last": 2.0,
                "confidence": 0.82,
                "as_of": "2026-11-15",
            },
            "non_technical": {
                "value": 59.5,
                "band": "solid",
                "delta_since_last": 0.0,
                "confidence": 0.55,
                "as_of": "2026-11-15",
            },
            "career_match_top": {
                "role_slug": "backend-engineer",
                "value": 76.4,
                "band": "strong",
            },
            "industry_demand": {
                "value": 71.0,
                "band": "strong",
                "snapshot_id": "snap-2026-11",
                "stale": False,
            },
            "job_readiness": {
                "role_slug": "backend-engineer",
                "value": 58.3,
                "band": "solid",
                "time_to_ready_weeks": [10, 16],
            },
        },
        dna={
            "archetype": [
                {"name": "Systems Builder", "pct": 0.62},
                {"name": "Applied Researcher", "pct": 0.21},
            ],
            "dimensions": {"technical_depth": 66, "systems_thinking": 72},
        },
        strengths=[{"label": "Python", "evidence": ["3 repos", "project work"], "percentile": 82}],
        gaps=[{
            "skill": "Docker",
            "current": 22,
            "required": 60,
            "priority": 0.81,
            "jrs_gain": 4.2,
            "est_hours": 18,
        }],
        target_roles=[{"slug": "backend-engineer", "cm": 76.4, "ids": 71.0, "jrs": 58.3}],
        data_quality={"completeness": 0.75, "stale_sources": [], "warnings": []},
    )
