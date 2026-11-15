from fastapi import APIRouter

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/unmapped-skills")
async def list_unmapped_skills():
    return {"unmapped": [], "total": 0}
