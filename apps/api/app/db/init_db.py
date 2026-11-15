import asyncio
from pathlib import Path
import yaml
from sqlalchemy.future import select
from app.db.session import engine, async_session_factory
from app.db.base import Base
from app.db.models import (
    User, Skill, UserSkill, SkillEvidence, Education, Experience, Project,
    Certification, ScoreRun, Score, DnaProfile, Roadmap, Milestone
)
from app.core.security import hash_password
from app.core.config import REPO_ROOT
import logging

logger = logging.getLogger(__name__)


async def init_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_factory() as session:
        # Check if default user exists
        res = await session.execute(select(User).where(User.email == "user@example.com"))
        user = res.scalars().first()

        if not user:
            logger.info("Seeding default demo user Alex Johnson...")
            user = User(
                email="user@example.com",
                password_hash=hash_password("password123"),
                display_name="Alex Johnson",
                role="user",
                country="global",
                currency="USD",
                locale="en",
                consent_flags={"data_processing": True, "telemetry": False, "ai_mentor": True},
                onboarding_state={"completed": True, "step": "dashboard"}
            )
            session.add(user)
            await session.flush()

            # Seed Education
            edu = Education(
                user_id=user.id,
                institution="State University of Technology",
                level="bachelors",
                degree="B.Tech Computer Science and Engineering",
                branch="Computer Science",
                start_year=2021,
                end_year=2025,
                status="completed",
                grade_type="cgpa10",
                grade_value=8.4,
                grade_normalized=84.0,
                relevant_courses=["Data Structures", "Algorithms", "Operating Systems", "Distributed Systems"]
            )
            session.add(edu)

            # Seed Experience
            exp = Experience(
                user_id=user.id,
                company="Nexus Software Labs",
                title="Software Engineer Intern",
                location="Remote",
                employment_type="internship",
                start_date="2024-05-01",
                end_date="2024-11-01",
                description="Designed asynchronous data ingestion pipelines with Python and FastAPI, deployed microservices with Docker.",
                skills_used=["python", "fastapi", "docker", "postgresql"]
            )
            session.add(exp)

            # Seed Projects
            proj1 = Project(
                user_id=user.id,
                title="Distributed Cache Proxy",
                description="High throughput in-memory caching system with consistent hashing, LRU eviction, and Prometheus metrics.",
                url="https://github.com/alex/cache-proxy",
                repo_url="https://github.com/alex/cache-proxy",
                skills_used=["python", "redis", "docker", "system-design"],
                verified=True
            )
            proj2 = Project(
                user_id=user.id,
                title="Career Twin Intelligence Platform",
                description="Full-stack career analytics dashboard built with Next.js, FastAPI, and Postgres pgvector.",
                url="https://github.com/alex/career-twin",
                repo_url="https://github.com/alex/career-twin",
                skills_used=["fastapi", "react", "typescript", "postgresql"],
                verified=True
            )
            session.add_all([proj1, proj2])

            # Seed Certifications
            cert = Certification(
                user_id=user.id,
                name="AWS Certified Solutions Architect - Associate",
                issuer="Amazon Web Services",
                issued_on="2024-08-15",
                expires_on="2027-08-15",
                credential_url="https://aws.amazon.com/verification",
                verified=True
            )
            session.add(cert)

            # Seed Skills and Evidence
            skills_data = [
                ("python", "Python", "backend", 82.0, 0.88),
                ("fastapi", "FastAPI", "backend", 75.0, 0.82),
                ("postgresql", "PostgreSQL", "backend", 62.0, 0.70),
                ("docker", "Docker", "cloud_devops", 42.0, 0.55),
                ("react", "React", "frontend", 58.0, 0.65),
                ("typescript", "TypeScript", "frontend", 54.0, 0.60),
                ("redis", "Redis", "backend", 50.0, 0.58),
                ("git", "Git", "cloud_devops", 85.0, 0.90),
                ("system-design", "System Design", "core_cs", 48.0, 0.50),
            ]

            for slug, name, cat, prof, conf in skills_data:
                skill_res = await session.execute(select(Skill).where(Skill.slug == slug))
                skill = skill_res.scalars().first()
                if not skill:
                    skill = Skill(slug=slug, name=name, category=cat, aliases=[slug])
                    session.add(skill)
                    await session.flush()

                user_skill = UserSkill(
                    user_id=user.id,
                    skill_id=skill.id,
                    proficiency=prof,
                    confidence=conf,
                    self_rating=round(prof / 20.0, 1)
                )
                session.add(user_skill)
                await session.flush()

                # Attach evidence
                ev = SkillEvidence(
                    user_skill_id=user_skill.id,
                    evidence_type="project" if prof > 60 else "experience",
                    signal_value=prof / 100.0,
                    weight=0.8,
                    reliability=0.9,
                    recency_date="2026-10-15",
                    metadata_json={"repo": "nexus-api", "commits_count": 42}
                )
                session.add(ev)

            # Seed initial ScoreRun
            score_run = ScoreRun(
                user_id=user.id,
                engine_version="1.0.0",
                taxonomy_version="1.0.0",
                input_hash="seed-initial-hash",
                config_hash="seed-cfg-hash",
                status="completed"
            )
            session.add(score_run)
            await session.flush()

            scores_to_add = [
                Score(score_run_id=score_run.id, kind="pps", value=74.5, band="solid", confidence=0.82, delta_since_last=3.1, explanation={"factors": [{"factor": "Verified project evidence", "impact": "+8.5"}]}),
                Score(score_run_id=score_run.id, kind="tss", value=68.0, band="solid", confidence=0.85, delta_since_last=2.0, explanation={"factors": [{"factor": "Python & FastAPI depth", "impact": "+14.0"}]}),
                Score(score_run_id=score_run.id, kind="ntss", value=64.0, band="solid", confidence=0.60, delta_since_last=0.0, explanation={"factors": [{"factor": "Internship technical collaboration", "impact": "+6.0"}]}),
                Score(score_run_id=score_run.id, kind="jrs", target_role_slug="backend-engineer", value=58.3, band="solid", confidence=0.78, delta_since_last=4.2, explanation={"factors": [{"factor": "Core backend skills matched", "impact": "+28.0"}], "data_gaps": ["Docker proficiency below 60% requirement"]}),
            ]
            session.add_all(scores_to_add)

            # Seed DNA
            dna = DnaProfile(
                user_id=user.id,
                score_run_id=score_run.id,
                dimensions={
                    "technical_depth": 78,
                    "systems_thinking": 72,
                    "execution_speed": 68,
                    "collaboration": 65,
                    "creative_exploration": 55,
                    "product_sense": 60,
                },
                archetype_weights=[
                    {"name": "Systems Builder", "pct": 0.62},
                    {"name": "Applied Researcher", "pct": 0.21},
                    {"name": "Product Craftsman", "pct": 0.17},
                ],
                narrative="Demonstrates strong architecture and systems foundation with rapidly growing backend proficiency."
            )
            session.add(dna)

            # Seed Roadmap
            roadmap = Roadmap(
                user_id=user.id,
                target_role_slug="backend-engineer",
                horizon_months=6,
                weekly_hours=8.0,
                status="active",
                params_json={"focus": "production_readiness"}
            )
            session.add(roadmap)
            await session.flush()

            milestones = [
                Milestone(
                    roadmap_id=roadmap.id,
                    sequence_order=1,
                    title="Containerization & Orchestration Foundation",
                    phase="Foundation",
                    month_index=1,
                    estimated_hours=18.0,
                    is_locked=False,
                    status="in_progress",
                    skills=["docker"],
                    resources=[{"title": "Docker Deep Dive", "type": "course", "url": "https://docker.com"}]
                ),
                Milestone(
                    roadmap_id=roadmap.id,
                    sequence_order=2,
                    title="Advanced PostgreSQL Indexing & Concurrency",
                    phase="Core",
                    month_index=2,
                    estimated_hours=20.0,
                    is_locked=False,
                    status="todo",
                    skills=["postgresql"],
                    resources=[{"title": "Use The Index, Luke", "type": "book", "url": "https://use-the-index-luke.com"}]
                ),
                Milestone(
                    roadmap_id=roadmap.id,
                    sequence_order=3,
                    title="Distributed Message Brokers with Kafka & Redis",
                    phase="Applied Projects",
                    month_index=3,
                    estimated_hours=25.0,
                    is_locked=False,
                    status="todo",
                    skills=["redis", "system-design"],
                    resources=[{"title": "Event-Driven Microservices in Python", "type": "project"}]
                ),
            ]
            session.add_all(milestones)

            await session.commit()
            logger.info("Default seed data initialized successfully.")
