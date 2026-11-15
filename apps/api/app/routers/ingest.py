from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, List
import datetime
from app.core.deps import get_db, get_current_user_id
from app.db.models import User, Skill, UserSkill, SkillEvidence
from app.services.ingestion.resume_parser import parse_resume_text
from app.routers.profile import resolve_user_id

router = APIRouter(prefix="/me/ingest", tags=["ingest"])


class ResumeUploadRequest(BaseModel):
    resume_text: str


@router.post("/resume")
async def ingest_resume(
    req: ResumeUploadRequest,
    user_id_str: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    u_id = await resolve_user_id(user_id_str, db)
    parsed = parse_resume_text(req.resume_text)

    skills_added = []
    for slug in parsed.get("extracted_skills", []):
        # Find or create skill
        skill_res = await db.execute(select(Skill).where(Skill.slug == slug))
        skill = skill_res.scalars().first()
        if not skill:
            skill = Skill(slug=slug, name=slug.capitalize(), category="backend", aliases=[slug])
            db.add(skill)
            await db.flush()

        # Check UserSkill
        us_res = await db.execute(select(UserSkill).where(UserSkill.user_id == u_id, UserSkill.skill_id == skill.id))
        user_skill = us_res.scalars().first()
        if not user_skill:
            user_skill = UserSkill(
                user_id=u_id,
                skill_id=skill.id,
                proficiency=65.0,
                confidence=0.70,
                self_rating=3.5
            )
            db.add(user_skill)
            await db.flush()

        ev = SkillEvidence(
            user_skill_id=user_skill.id,
            evidence_type="resume_parse",
            signal_value=0.70,
            weight=0.75,
            reliability=0.85,
            recency_date=datetime.date.today().isoformat(),
            metadata_json={"source": "resume_parser"}
        )
        db.add(ev)
        skills_added.append(slug)

    await db.commit()
    return {
        "status": "success",
        "skills_extracted_count": len(skills_added),
        "skills": skills_added,
        "education_detected": parsed["education_detected"],
        "experience_detected": parsed["experience_detected"],
        "confidence": parsed["confidence"]
    }
