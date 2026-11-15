from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import datetime
from app.core.deps import get_db, get_current_user_id
from app.db.models import User, Skill, UserSkill, SkillEvidence
from app.services.skills.proficiency import estimate_proficiency, SkillEvidenceItem, ProficiencyConfig
from app.core.config import scoring_config
from app.routers.profile import resolve_user_id
import uuid

router = APIRouter(prefix="/me/skills", tags=["skills"])


class AddSkillRequest(BaseModel):
    skill_slug: str
    evidence_type: str = "project" # project, experience, github, certification, assessment
    signal_value: float = 0.70    # 0 to 1
    self_rating: Optional[float] = 3.5 # 1 to 5


class SelfRateRequest(BaseModel):
    skill_slug: str
    rating: float # 1 to 5


@router.get("")
async def get_user_skills(user_id_str: str = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    u_id = await resolve_user_id(user_id_str, db)

    res = await db.execute(
        select(UserSkill)
        .where(UserSkill.user_id == u_id)
        .options(selectinload(UserSkill.evidence_items))
    )
    user_skills = res.scalars().all()

    # Load all canonical skills
    all_skills = {s.id: s for s in (await db.execute(select(Skill))).scalars().all()}

    output = []
    for us in user_skills:
        skill_obj = all_skills.get(us.skill_id)
        slug = skill_obj.slug if skill_obj else "unknown"
        name = skill_obj.name if skill_obj else slug.capitalize()
        category = skill_obj.category if skill_obj else "backend"

        output.append({
            "id": str(us.id),
            "skill_slug": slug,
            "name": name,
            "category": category,
            "proficiency": us.proficiency,
            "confidence": us.confidence,
            "self_rating": us.self_rating or 3.5,
            "evidence_count": len(us.evidence_items),
        })

    return output


@router.post("/add")
async def add_or_update_skill(req: AddSkillRequest, user_id_str: str = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    u_id = await resolve_user_id(user_id_str, db)

    # Find canonical skill or create
    skill_res = await db.execute(select(Skill).where(Skill.slug == req.skill_slug.lower()))
    skill = skill_res.scalars().first()
    if not skill:
        skill = Skill(slug=req.skill_slug.lower(), name=req.skill_slug.capitalize(), category="backend", aliases=[req.skill_slug.lower()])
        db.add(skill)
        await db.flush()

    # Find UserSkill
    us_res = await db.execute(select(UserSkill).where(UserSkill.user_id == u_id, UserSkill.skill_id == skill.id).options(selectinload(UserSkill.evidence_items)))
    user_skill = us_res.scalars().first()

    if not user_skill:
        user_skill = UserSkill(
            user_id=u_id,
            skill_id=skill.id,
            proficiency=req.signal_value * 100.0,
            confidence=0.60,
            self_rating=req.self_rating
        )
        db.add(user_skill)
        await db.flush()
    else:
        if req.self_rating:
            user_skill.self_rating = req.self_rating

    # Add evidence item
    ev = SkillEvidence(
        user_skill_id=user_skill.id,
        evidence_type=req.evidence_type,
        signal_value=req.signal_value,
        weight=0.8,
        reliability=0.9,
        recency_date=datetime.date.today().isoformat(),
        metadata_json={"source": "user_submission"}
    )
    db.add(ev)
    await db.flush()

    # Re-estimate proficiency using pure algorithm
    cfg = ProficiencyConfig(
        half_life_months=scoring_config.get("half_life_months", {}),
        confidence_norm=scoring_config.get("confidence_norm", 1.5)
    )

    evidence_items = [
        SkillEvidenceItem(
            skill_slug=skill.slug,
            category=skill.category,
            evidence_type=item.evidence_type,
            weight=item.weight,
            signal_value=item.signal_value,
            recency_date=datetime.date.fromisoformat(item.recency_date),
            reliability=item.reliability
        )
        for item in user_skill.evidence_items
    ]
    evidence_items.append(
        SkillEvidenceItem(
            skill_slug=skill.slug,
            category=skill.category,
            evidence_type=req.evidence_type,
            weight=0.8,
            signal_value=req.signal_value,
            recency_date=datetime.date.today(),
            reliability=0.9
        )
    )

    p, conf = estimate_proficiency(evidence_items, cfg, datetime.date.today())
    user_skill.proficiency = p
    user_skill.confidence = conf

    await db.commit()
    return {"skill_slug": skill.slug, "proficiency": p, "confidence": conf}


@router.get("/taxonomy")
async def get_taxonomy_skills(db: AsyncSession = Depends(get_db)):
    skills = (await db.execute(select(Skill))).scalars().all()
    return skills
