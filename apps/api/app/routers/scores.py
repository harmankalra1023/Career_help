from fastapi import APIRouter, Depends
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from typing import Dict, Any, List
import datetime
from app.core.deps import get_db, get_current_user_id
from app.db.models import (
    User, Skill, UserSkill, Education, Experience, Project, Certification,
    ScoreRun, Score, DnaProfile, AssessmentResponse
)
from app.services.scoring.engine import (
    compute_pps, compute_tss, compute_ntss, compute_jrs, compute_dna_archetypes
)
from app.services.matching.career_match import match_role
from app.routers.profile import resolve_user_id
from app.core.config import scoring_config

router = APIRouter(prefix="/me", tags=["scores"])


@router.get("/dashboard")
async def get_dashboard(user_id_str: str = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    u_id = await resolve_user_id(user_id_str, db)

    # 1. Fetch latest score run and scores
    score_run_res = await db.execute(
        select(ScoreRun)
        .where(ScoreRun.user_id == u_id)
        .order_by(ScoreRun.created_at.desc())
        .options(selectinload(ScoreRun.scores))
    )
    latest_run = score_run_res.scalars().first()

    # 2. Fetch DNA profile
    dna_res = await db.execute(
        select(DnaProfile).where(DnaProfile.user_id == u_id).order_by(DnaProfile.created_at.desc())
    )
    dna_profile = dna_res.scalars().first()

    # 3. Fetch User Skills
    us_res = await db.execute(select(UserSkill).where(UserSkill.user_id == u_id))
    user_skills = us_res.scalars().all()

    all_skills = {s.id: s for s in (await db.execute(select(Skill))).scalars().all()}
    skills_map = {all_skills[us.skill_id].slug: us.proficiency for us in user_skills if us.skill_id in all_skills}

    # Extract score values
    scores_dict = {}
    if latest_run and latest_run.scores:
        for s in latest_run.scores:
            scores_dict[s.kind] = {
                "value": s.value,
                "band": s.band,
                "delta_since_last": s.delta_since_last or 0.0,
                "confidence": s.confidence,
                "as_of": s.created_at.strftime("%Y-%m-%d"),
                "explanation": s.explanation,
            }

    # Fallbacks if score run empty
    if "pps" not in scores_dict:
        scores_dict["pps"] = {"value": 74.5, "band": "solid", "delta_since_last": 3.1, "confidence": 0.82, "as_of": "2026-11-15"}
    if "tss" not in scores_dict:
        scores_dict["tss"] = {"value": 68.0, "band": "solid", "delta_since_last": 2.0, "confidence": 0.85, "as_of": "2026-11-15"}
    if "ntss" not in scores_dict:
        scores_dict["ntss"] = {"value": 64.0, "band": "solid", "delta_since_last": 0.0, "confidence": 0.60, "as_of": "2026-11-15"}
    if "jrs" not in scores_dict:
        scores_dict["jrs"] = {"value": 58.3, "band": "solid", "delta_since_last": 4.2, "confidence": 0.78, "as_of": "2026-11-15"}

    # DNA data
    dna_data = {
        "dimensions": dna_profile.dimensions if dna_profile else {"technical_depth": 78, "systems_thinking": 72, "execution_speed": 68, "collaboration": 65, "creative_exploration": 55, "product_sense": 60},
        "archetype": dna_profile.archetype_weights if dna_profile else [{"name": "Systems Builder", "pct": 0.62}, {"name": "Applied Researcher", "pct": 0.21}],
        "narrative": dna_profile.narrative if dna_profile else "Demonstrates strong architecture and systems foundation."
    }

    # Top strengths
    strengths = [
        {"label": "Python", "evidence": ["Nexus API microservice", "Cache proxy repository"], "percentile": 85},
        {"label": "FastAPI", "evidence": ["Async API endpoints", "OpenAPI schemas"], "percentile": 82},
        {"label": "Git", "evidence": ["Production commit history", "Branch workflows"], "percentile": 88},
    ]

    # Priority gaps for backend engineer
    gaps = [
        {"skill": "Docker", "current": skills_map.get("docker", 42.0), "required": 60.0, "priority": 0.82, "jrs_gain": 4.2, "est_hours": 18},
        {"skill": "PostgreSQL", "current": skills_map.get("postgresql", 62.0), "required": 70.0, "priority": 0.65, "jrs_gain": 2.8, "est_hours": 14},
    ]

    return {
        "scores": {
            "profile": scores_dict["pps"],
            "technical": scores_dict["tss"],
            "non_technical": scores_dict["ntss"],
            "job_readiness": scores_dict["jrs"],
            "career_match_top": {"role_slug": "backend-engineer", "value": 76.4, "band": "strong"},
            "industry_demand": {"value": 71.0, "band": "strong", "snapshot_id": "snap-2026-11", "stale": False},
        },
        "dna": dna_data,
        "strengths": strengths,
        "gaps": gaps,
        "target_roles": [{"slug": "backend-engineer", "cm": 76.4, "ids": 71.0, "jrs": 58.3}],
        "data_quality": {"completeness": 0.85, "stale_sources": [], "warnings": []}
    }


@router.post("/twin/generate")
async def generate_twin(user_id_str: str = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    """
    Executes full Digital Career Twin recomputation workflow (PRD §5, Technical Design §2.3).
    """
    u_id = await resolve_user_id(user_id_str, db)

    # 1. Gather all profile evidence
    edus = (await db.execute(select(Education).where(Education.user_id == u_id))).scalars().all()
    exps = (await db.execute(select(Experience).where(Experience.user_id == u_id))).scalars().all()
    projs = (await db.execute(select(Project).where(Project.user_id == u_id))).scalars().all()
    certs = (await db.execute(select(Certification).where(Certification.user_id == u_id))).scalars().all()
    user_skills = (await db.execute(select(UserSkill).where(UserSkill.user_id == u_id))).scalars().all()
    assessments = (await db.execute(select(AssessmentResponse).where(AssessmentResponse.user_id == u_id))).scalars().all()

    all_skills = {s.id: s for s in (await db.execute(select(Skill))).scalars().all()}
    skill_list = [
        {"slug": all_skills[us.skill_id].slug, "name": all_skills[us.skill_id].name, "category": all_skills[us.skill_id].category, "proficiency": us.proficiency, "confidence": us.confidence}
        for us in user_skills if us.skill_id in all_skills
    ]
    skills_map = {s["slug"]: s["proficiency"] for s in skill_list}

    # Completeness calculation
    completeness = min(1.0, (len(edus) * 0.15 + len(exps) * 0.25 + len(projs) * 0.25 + len(certs) * 0.10 + len(user_skills) * 0.05))

    # Traits calculation
    traits = {"conscientiousness": 70.0, "agreeableness": 65.0, "emotional_stability": 68.0, "extraversion": 55.0}
    for ass in assessments:
        traits.update(ass.trait_scores)

    # Pure score computations
    pps_out = compute_pps(completeness, 0.75, 0.80)
    tss_out = compute_tss(skill_list)
    ntss_out = compute_ntss(traits, len(exps))

    role_reqs = [
        {"skill_slug": "python", "minimum_level": 60.0},
        {"skill_slug": "fastapi", "minimum_level": 55.0},
        {"skill_slug": "postgresql", "minimum_level": 50.0},
        {"skill_slug": "docker", "minimum_level": 40.0},
    ]
    jrs_out = compute_jrs(skills_map, role_reqs)

    dimensions = {
        "technical_depth": min(100.0, tss_out.value + 5.0),
        "systems_thinking": min(100.0, tss_out.value - 2.0),
        "execution_speed": min(100.0, pps_out.value),
        "collaboration": min(100.0, ntss_out.value),
        "creative_exploration": 60.0,
        "product_sense": 65.0,
    }
    archetypes, narrative = compute_dna_archetypes(dimensions)

    # Persist score run
    score_run = ScoreRun(
        user_id=u_id,
        engine_version="1.0.0",
        taxonomy_version="1.0.0",
        input_hash=f"run-{datetime.datetime.utcnow().timestamp()}",
        config_hash="cfg-active",
        status="completed"
    )
    db.add(score_run)
    await db.flush()

    new_scores = [
        Score(score_run_id=score_run.id, kind="pps", value=pps_out.value, band=pps_out.band, confidence=pps_out.confidence, explanation={"factors": pps_out.factors, "data_gaps": pps_out.data_gaps}),
        Score(score_run_id=score_run.id, kind="tss", value=tss_out.value, band=tss_out.band, confidence=tss_out.confidence, explanation={"factors": tss_out.factors, "data_gaps": tss_out.data_gaps}),
        Score(score_run_id=score_run.id, kind="ntss", value=ntss_out.value, band=ntss_out.band, confidence=ntss_out.confidence, explanation={"factors": ntss_out.factors, "data_gaps": ntss_out.data_gaps}),
        Score(score_run_id=score_run.id, kind="jrs", target_role_slug="backend-engineer", value=jrs_out.value, band=jrs_out.band, confidence=jrs_out.confidence, explanation={"factors": jrs_out.factors, "data_gaps": jrs_out.data_gaps}),
    ]
    db.add_all(new_scores)

    dna = DnaProfile(
        user_id=u_id,
        score_run_id=score_run.id,
        dimensions=dimensions,
        archetype_weights=archetypes,
        narrative=narrative
    )
    db.add(dna)
    await db.commit()

    return {
        "status": "success",
        "score_run_id": str(score_run.id),
        "scores": {
            "pps": pps_out.value,
            "tss": tss_out.value,
            "ntss": ntss_out.value,
            "jrs": jrs_out.value,
        },
        "archetypes": archetypes
    }
