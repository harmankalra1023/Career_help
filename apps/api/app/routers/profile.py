from fastapi import APIRouter, Depends
from app.core.deps import get_current_user_id
from app.schemas.profile import ProfileCompletenessResponse

router = APIRouter(prefix="/me/profile", tags=["profile"])


@router.get("/completeness", response_model=ProfileCompletenessResponse)
async def get_completeness(user_id: str = Depends(get_current_user_id)):
    return ProfileCompletenessResponse(
        completeness=0.75,
        completed_sections=["education", "skills", "projects"],
        missing_sections=["assessments", "certifications"]
    )
