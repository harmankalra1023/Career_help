from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any
from app.core.deps import get_db, get_current_user_id
from app.db.models import User, Education, Experience, Project, Certification, UserSkill
from app.schemas.profile import ProfileCompletenessResponse, EducationCreate, ExperienceCreate, ProjectCreate
import uuid

router = APIRouter(prefix="/me/profile", tags=["profile"])


async def resolve_user_id(user_id_str: str, db: AsyncSession) -> uuid.UUID:
    try:
        return uuid.UUID(user_id_str)
    except Exception:
        res = await db.execute(select(User).where(User.email == "user@example.com"))
        user = res.scalars().first()
        return user.id if user else uuid.uuid4()


@router.get("")
async def get_full_profile(user_id_str: str = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    u_id = await resolve_user_id(user_id_str, db)

    edus = (await db.execute(select(Education).where(Education.user_id == u_id))).scalars().all()
    exps = (await db.execute(select(Experience).where(Experience.user_id == u_id))).scalars().all()
    projs = (await db.execute(select(Project).where(Project.user_id == u_id))).scalars().all()
    certs = (await db.execute(select(Certification).where(Certification.user_id == u_id))).scalars().all()

    return {
        "education": edus,
        "experiences": exps,
        "projects": projs,
        "certifications": certs,
    }


@router.get("/completeness", response_model=ProfileCompletenessResponse)
async def get_completeness(user_id_str: str = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    u_id = await resolve_user_id(user_id_str, db)

    has_edu = bool((await db.execute(select(Education).where(Education.user_id == u_id))).first())
    has_exp = bool((await db.execute(select(Experience).where(Experience.user_id == u_id))).first())
    has_proj = bool((await db.execute(select(Project).where(Project.user_id == u_id))).first())
    has_cert = bool((await db.execute(select(Certification).where(Certification.user_id == u_id))).first())
    has_skills = bool((await db.execute(select(UserSkill).where(UserSkill.user_id == u_id))).first())

    # Weights per PRD §8.1: Experience (25%), Projects (25%), Skills (20%), Education (15%), Certifications (10%), Assessments (5%)
    score = 0.0
    completed = []
    missing = []

    if has_edu:
        score += 0.15
        completed.append("Education")
    else:
        missing.append("Education")

    if has_exp:
        score += 0.25
        completed.append("Experience")
    else:
        missing.append("Experience")

    if has_proj:
        score += 0.25
        completed.append("Projects")
    else:
        missing.append("Projects")

    if has_skills:
        score += 0.20
        completed.append("Skills")
    else:
        missing.append("Skills")

    if has_cert:
        score += 0.10
        completed.append("Certifications")
    else:
        missing.append("Certifications")

    # Assessment credit default 0.05
    score += 0.05
    completed.append("Assessments")

    return ProfileCompletenessResponse(
        completeness=round(score, 2),
        completed_sections=completed,
        missing_sections=missing
    )


@router.post("/education")
async def add_education(edu: EducationCreate, user_id_str: str = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    u_id = await resolve_user_id(user_id_str, db)
    new_edu = Education(
        user_id=u_id,
        institution=edu.institution,
        level=edu.level,
        degree=edu.degree,
        branch=edu.branch,
        start_year=edu.start_year,
        end_year=edu.end_year,
        status=edu.status,
        grade_type=edu.grade_type,
        grade_value=edu.grade_value,
        grade_normalized=edu.grade_normalized or 80.0,
        relevant_courses=edu.relevant_courses
    )
    db.add(new_edu)
    await db.commit()
    await db.refresh(new_edu)
    return new_edu


@router.post("/experience")
async def add_experience(exp: ExperienceCreate, user_id_str: str = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    u_id = await resolve_user_id(user_id_str, db)
    new_exp = Experience(
        user_id=u_id,
        company=exp.company,
        title=exp.title,
        location=exp.location,
        employment_type=exp.employment_type,
        start_date=exp.start_date,
        end_date=exp.end_date,
        description=exp.description,
        skills_used=exp.skills_used
    )
    db.add(new_exp)
    await db.commit()
    await db.refresh(new_exp)
    return new_exp


@router.post("/projects")
async def add_project(proj: ProjectCreate, user_id_str: str = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    u_id = await resolve_user_id(user_id_str, db)
    new_proj = Project(
        user_id=u_id,
        title=proj.title,
        description=proj.description,
        url=proj.url,
        repo_url=proj.repo_url,
        skills_used=proj.skills_used,
        verified=bool(proj.repo_url)
    )
    db.add(new_proj)
    await db.commit()
    await db.refresh(new_proj)
    return new_proj
