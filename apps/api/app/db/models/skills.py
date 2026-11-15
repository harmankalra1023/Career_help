import uuid
from typing import Optional, List, Dict, Any
from sqlalchemy import String, Float, ForeignKey, JSON, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, TimestampMixin


class Skill(Base, TimestampMixin):
    __tablename__ = "skills"

    slug: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(String(2000), nullable=True)
    aliases: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)


class UserSkill(Base, TimestampMixin):
    __tablename__ = "user_skills"
    __table_args__ = (UniqueConstraint("user_id", "skill_id", name="uq_user_skill"),)

    user_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    skill_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("skills.id", ondelete="CASCADE"), nullable=False, index=True)
    proficiency: Mapped[float] = mapped_column(Float, default=0.0, nullable=False) # 0 to 100
    confidence: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)  # 0 to 1
    self_rating: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    evidence_items: Mapped[List["SkillEvidence"]] = relationship("SkillEvidence", back_populates="user_skill", cascade="all, delete-orphan")


class SkillEvidence(Base, TimestampMixin):
    __tablename__ = "skill_evidence"

    user_skill_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("user_skills.id", ondelete="CASCADE"), nullable=False, index=True)
    evidence_type: Mapped[str] = mapped_column(String(50), nullable=False) # github, experience, assessment, etc.
    signal_value: Mapped[float] = mapped_column(Float, nullable=False) # 0 to 1
    weight: Mapped[float] = mapped_column(Float, nullable=False)
    reliability: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    recency_date: Mapped[str] = mapped_column(String(20), nullable=False) # ISO date string YYYY-MM-DD
    metadata_json: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    user_skill: Mapped["UserSkill"] = relationship("UserSkill", back_populates="evidence_items")
