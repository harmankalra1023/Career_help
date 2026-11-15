from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, List
from pydantic import BaseModel
import yaml
from pathlib import Path
from app.core.deps import get_db, get_current_user_id
from app.db.models import AssessmentResponse
from app.services.assessments.engine import score_assessment
from app.routers.profile import resolve_user_id
from app.core.config import REPO_ROOT

router = APIRouter(prefix="/assessments", tags=["assessments"])


class SubmitAssessmentRequest(BaseModel):
    instrument_id: str
    answers: Dict[str, int] # item_id -> 1..5


def load_question_bank(instrument_id: str) -> Dict[str, Any]:
    file_name = f"{instrument_id}.yaml"
    path = REPO_ROOT / "packages" / "question-banks" / file_name
    if not path.exists():
        path = Path("packages/question-banks") / file_name
    if not path.exists():
        return {"items": [], "scale": {"min": 1, "max": 5}}
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


@router.get("/instruments")
async def list_instruments():
    return [
        {
            "id": "big5",
            "name": "Big Five Personality (IPIP-50)",
            "description": "Measures Extraversion, Agreeableness, Conscientiousness, Emotional Stability, and Openness.",
            "questions_count": 10,
            "estimated_minutes": 5
        },
        {
            "id": "riasec",
            "name": "Holland Occupational Interests (RIASEC)",
            "description": "Identifies career interest alignments across Realistic, Investigative, Artistic, Social, Enterprising, and Conventional domains.",
            "questions_count": 6,
            "estimated_minutes": 3
        }
    ]


@router.get("/questions/{instrument_id}")
async def get_questions(instrument_id: str):
    data = load_question_bank(instrument_id)
    if not data.get("items"):
        raise HTTPException(status_code=404, detail="Question bank not found")
    return {
        "instrument_id": instrument_id,
        "scale": data.get("scale", {"min": 1, "max": 5}),
        "items": data.get("items", [])
    }


@router.post("/submit")
async def submit_assessment(
    req: SubmitAssessmentRequest,
    user_id_str: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    u_id = await resolve_user_id(user_id_str, db)
    bank_data = load_question_bank(req.instrument_id)
    items = bank_data.get("items", [])

    if not items:
        raise HTTPException(status_code=400, detail="Invalid instrument")

    # Score assessment
    trait_scores = score_assessment(req.instrument_id, req.answers, items)

    # Save to db
    resp = AssessmentResponse(
        user_id=u_id,
        instrument_id=req.instrument_id,
        answers_json=req.answers,
        trait_scores=trait_scores
    )
    db.add(resp)
    await db.commit()

    return {
        "status": "completed",
        "instrument_id": req.instrument_id,
        "trait_scores": trait_scores
    }
