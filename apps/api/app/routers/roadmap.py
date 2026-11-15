from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from typing import List, Dict, Any
from pydantic import BaseModel
from app.core.deps import get_db, get_current_user_id
from app.db.models import User, Skill, UserSkill, Roadmap, Milestone
from app.services.planner.roadmap_planner import generate_roadmap
from app.services.matching.career_match import match_role
from app.routers.careers import ROLES_TAXONOMY
from app.routers.profile import resolve_user_id
import uuid

router = APIRouter(prefix="/me/roadmaps", tags=["roadmap"])


class CreateRoadmapRequest(BaseModel):
    target_role: str = "backend-engineer"
    weekly_hours: float = 8.0
    horizon_months: int = 6


class MilestoneUpdate(BaseModel):
    status: str # todo, in_progress, completed


@router.get("/current")
async def get_current_roadmap(user_id_str: str = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    u_id = await resolve_user_id(user_id_str, db)

    res = await db.execute(
        select(Roadmap)
        .where(Roadmap.user_id == u_id, Roadmap.status == "active")
        .order_by(Roadmap.created_at.desc())
        .options(selectinload(Roadmap.milestones))
    )
    roadmap = res.scalars().first()

    if not roadmap:
        return {"roadmap": None, "milestones": []}

    sorted_milestones = sorted(roadmap.milestones, key=lambda m: m.sequence_order)
    return {
        "id": str(roadmap.id),
        "target_role_slug": roadmap.target_role_slug,
        "horizon_months": roadmap.horizon_months,
        "weekly_hours": roadmap.weekly_hours,
        "milestones": [
            {
                "id": str(m.id),
                "sequence_order": m.sequence_order,
                "title": m.title,
                "phase": m.phase,
                "month_index": m.month_index,
                "estimated_hours": m.estimated_hours,
                "is_locked": m.is_locked,
                "status": m.status,
                "skills": m.skills,
                "resources": m.resources,
            }
            for m in sorted_milestones
        ]
    }


@router.post("")
async def create_new_roadmap(
    req: CreateRoadmapRequest,
    user_id_str: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    u_id = await resolve_user_id(user_id_str, db)

    # Calculate gaps for target role
    role = next((r for r in ROLES_TAXONOMY if r["slug"] == req.target_role), ROLES_TAXONOMY[0])

    user_skills = (await db.execute(select(UserSkill).where(UserSkill.user_id == u_id))).scalars().all()
    all_skills = {s.id: s for s in (await db.execute(select(Skill))).scalars().all()}
    skills_map = {all_skills[us.skill_id].slug: us.proficiency for us in user_skills if us.skill_id in all_skills}

    match_data = match_role(skills_map, {}, role)
    gaps = match_data.get("gaps", [])

    planned_milestones = generate_roadmap(
        target_role=req.target_role,
        gaps=gaps,
        weekly_hours=req.weekly_hours,
        horizon_months=req.horizon_months
    )

    # Deactivate previous roadmaps
    prev_res = await db.execute(select(Roadmap).where(Roadmap.user_id == u_id, Roadmap.status == "active"))
    for prev in prev_res.scalars().all():
        prev.status = "archived"

    new_roadmap = Roadmap(
        user_id=u_id,
        target_role_slug=req.target_role,
        horizon_months=req.horizon_months,
        weekly_hours=req.weekly_hours,
        status="active",
        params_json={"generated_gaps_count": len(gaps)}
    )
    db.add(new_roadmap)
    await db.flush()

    db_milestones = [
        Milestone(
            roadmap_id=new_roadmap.id,
            sequence_order=m["sequence_order"],
            title=m["title"],
            phase=m["phase"],
            month_index=m["month_index"],
            estimated_hours=m["estimated_hours"],
            is_locked=m["is_locked"],
            status=m["status"],
            skills=m["skills"],
            resources=m["resources"]
        )
        for m in planned_milestones
    ]
    db.add_all(db_milestones)
    await db.commit()

    return {"status": "created", "roadmap_id": str(new_roadmap.id), "milestones_count": len(db_milestones)}


@router.patch("/milestones/{milestone_id}")
async def update_milestone_status(
    milestone_id: str,
    update: MilestoneUpdate,
    user_id_str: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    try:
        m_id = uuid.UUID(milestone_id)
        res = await db.execute(select(Milestone).where(Milestone.id == m_id))
        milestone = res.scalars().first()
    except Exception:
        milestone = None

    if not milestone:
        raise HTTPException(status_code=404, detail="Milestone not found")

    milestone.status = update.status
    await db.commit()
    return {"id": str(milestone.id), "status": milestone.status}
