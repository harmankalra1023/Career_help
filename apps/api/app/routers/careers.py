from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any
from app.core.deps import get_db, get_current_user_id
from app.db.models import User, Skill, UserSkill
from app.services.matching.career_match import match_role
from app.routers.profile import resolve_user_id

router = APIRouter(prefix="/careers", tags=["careers"])

# Curated reference roles taxonomy
ROLES_TAXONOMY = [
    {
        "slug": "backend-engineer",
        "title": "Backend Engineer",
        "description": "Designs, develops, and maintains server-side architecture, APIs, and data layers.",
        "category": "Software Engineering",
        "demand_score": 78.0,
        "salary_range": "$95k – $160k",
        "required_skills": [
            {"skill_slug": "python", "minimum_level": 65.0, "importance": 0.95},
            {"skill_slug": "fastapi", "minimum_level": 60.0, "importance": 0.85},
            {"skill_slug": "postgresql", "minimum_level": 60.0, "importance": 0.85},
            {"skill_slug": "docker", "minimum_level": 55.0, "importance": 0.75},
            {"skill_slug": "redis", "minimum_level": 50.0, "importance": 0.65},
            {"skill_slug": "system-design", "minimum_level": 55.0, "importance": 0.70},
        ],
        "riasec": {"realistic": 0.5, "investigative": 0.8, "artistic": 0.2, "social": 0.3, "enterprising": 0.4, "conventional": 0.7}
    },
    {
        "slug": "full-stack-engineer",
        "title": "Full Stack Engineer",
        "description": "Constructs end-to-end web applications bridging rich client user interfaces and scalable backends.",
        "category": "Software Engineering",
        "demand_score": 82.0,
        "salary_range": "$90k – $155k",
        "required_skills": [
            {"skill_slug": "react", "minimum_level": 65.0, "importance": 0.90},
            {"skill_slug": "typescript", "minimum_level": 60.0, "importance": 0.85},
            {"skill_slug": "fastapi", "minimum_level": 55.0, "importance": 0.80},
            {"skill_slug": "postgresql", "minimum_level": 50.0, "importance": 0.75},
            {"skill_slug": "docker", "minimum_level": 45.0, "importance": 0.60},
        ],
        "riasec": {"realistic": 0.4, "investigative": 0.7, "artistic": 0.6, "social": 0.4, "enterprising": 0.5, "conventional": 0.6}
    },
    {
        "slug": "devops-engineer",
        "title": "DevOps / Platform Engineer",
        "description": "Automates cloud infrastructure, CI/CD pipelines, container orchestration, and observability.",
        "category": "Infrastructure & Cloud",
        "demand_score": 85.0,
        "salary_range": "$105k – $175k",
        "required_skills": [
            {"skill_slug": "docker", "minimum_level": 75.0, "importance": 0.95},
            {"skill_slug": "kubernetes", "minimum_level": 65.0, "importance": 0.90},
            {"skill_slug": "python", "minimum_level": 60.0, "importance": 0.75},
            {"skill_slug": "system-design", "minimum_level": 65.0, "importance": 0.80},
        ],
        "riasec": {"realistic": 0.7, "investigative": 0.7, "artistic": 0.1, "social": 0.3, "enterprising": 0.4, "conventional": 0.8}
    },
    {
        "slug": "ai-application-engineer",
        "title": "AI Application Engineer",
        "description": "Builds production applications powered by Large Language Models, embeddings, and vector databases.",
        "category": "Artificial Intelligence",
        "demand_score": 92.0,
        "salary_range": "$115k – $190k",
        "required_skills": [
            {"skill_slug": "python", "minimum_level": 75.0, "importance": 0.95},
            {"skill_slug": "fastapi", "minimum_level": 65.0, "importance": 0.85},
            {"skill_slug": "system-design", "minimum_level": 60.0, "importance": 0.80},
            {"skill_slug": "docker", "minimum_level": 50.0, "importance": 0.65},
        ],
        "riasec": {"realistic": 0.4, "investigative": 0.9, "artistic": 0.5, "social": 0.3, "enterprising": 0.5, "conventional": 0.5}
    }
]


@router.get("")
async def list_matched_careers(user_id_str: str = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    u_id = await resolve_user_id(user_id_str, db)

    # Load user skills
    user_skills = (await db.execute(select(UserSkill).where(UserSkill.user_id == u_id))).scalars().all()
    all_skills = {s.id: s for s in (await db.execute(select(Skill))).scalars().all()}
    skills_map = {all_skills[us.skill_id].slug: us.proficiency for us in user_skills if us.skill_id in all_skills}

    results = []
    for role in ROLES_TAXONOMY:
        match_data = match_role(skills_map, {"investigative": 0.8, "realistic": 0.6}, role)
        results.append({
            "slug": role["slug"],
            "title": role["title"],
            "description": role["description"],
            "category": role["category"],
            "demand_score": role["demand_score"],
            "salary_range": role["salary_range"],
            "match_score": match_data["match_score"],
            "band": match_data["band"],
            "skill_fit": match_data["skill_fit"],
            "gap_count": len(match_data["gaps"]),
        })

    return sorted(results, key=lambda r: r["match_score"], reverse=True)


@router.get("/{slug}")
async def get_career_detail(slug: str, user_id_str: str = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    role = next((r for r in ROLES_TAXONOMY if r["slug"] == slug), None)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    u_id = await resolve_user_id(user_id_str, db)
    user_skills = (await db.execute(select(UserSkill).where(UserSkill.user_id == u_id))).scalars().all()
    all_skills = {s.id: s for s in (await db.execute(select(Skill))).scalars().all()}
    skills_map = {all_skills[us.skill_id].slug: us.proficiency for us in user_skills if us.skill_id in all_skills}

    match_data = match_role(skills_map, {"investigative": 0.8, "realistic": 0.6}, role)

    return {
        **role,
        "match_score": match_data["match_score"],
        "band": match_data["band"],
        "skill_fit": match_data["skill_fit"],
        "gaps": match_data["gaps"],
        "transferable_strengths": [
            {"skill": s, "proficiency": skills_map[s]}
            for s in skills_map if s in [req["skill_slug"] for req in role["required_skills"]] and skills_map[s] >= 60.0
        ]
    }
