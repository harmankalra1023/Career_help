from fastapi import APIRouter

router = APIRouter(prefix="/careers", tags=["careers"])


@router.get("")
async def list_careers():
    return [
        {"slug": "backend-engineer", "title": "Backend Engineer", "match_score": 76.4},
        {"slug": "frontend-engineer", "title": "Frontend Engineer", "match_score": 68.2},
    ]


@router.get("/{slug}")
async def get_career_detail(slug: str):
    return {
        "slug": slug,
        "title": "Backend Engineer",
        "description": "Designs and develops backend services and data layers.",
        "match_score": 76.4,
        "demand_score": 71.0,
        "readiness_score": 58.3,
    }
