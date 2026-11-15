from fastapi import APIRouter

router = APIRouter(prefix="/assessments", tags=["assessments"])


@router.get("/instruments")
async def list_instruments():
    return [
        {"id": "big5", "name": "Big Five Personality", "questions_count": 50},
        {"id": "riasec", "name": "Holland RIASEC Occupational Interest", "questions_count": 30},
        {"id": "work_style", "name": "Work Style Inventory", "questions_count": 20},
    ]
