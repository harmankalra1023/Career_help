from fastapi import APIRouter, Depends
from app.core.deps import get_current_user_id
from app.schemas.roadmap import RoadmapCreateRequest, RoadmapResponse

router = APIRouter(prefix="/me/roadmaps", tags=["roadmap"])


@router.post("", response_model=RoadmapResponse)
async def create_roadmap(req: RoadmapCreateRequest, user_id: str = Depends(get_current_user_id)):
    return RoadmapResponse(
        id="road-001",
        target_role_slug=req.target_role,
        horizon_months=req.horizon_months,
        weekly_hours=req.weekly_hours,
        milestones=[
            {
                "id": "ms-01",
                "sequence_order": 1,
                "title": "Foundation: Docker and Containerization",
                "phase": "Foundation",
                "month_index": 1,
                "estimated_hours": 18.0,
                "is_locked": False,
                "status": "todo",
                "skills": ["docker"],
                "resources": [{"title": "Docker Hands-on Workshop", "type": "course"}],
            }
        ],
    )
