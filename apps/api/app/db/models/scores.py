import uuid
from typing import Optional, Dict, Any, List
from sqlalchemy import String, Float, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, TimestampMixin


class ScoreRun(Base, TimestampMixin):
    __tablename__ = "score_runs"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    engine_version: Mapped[str] = mapped_column(String(50), nullable=False)
    taxonomy_version: Mapped[str] = mapped_column(String(50), nullable=False)
    input_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    config_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="completed", nullable=False)

    scores: Mapped[List["Score"]] = relationship("Score", back_populates="score_run", cascade="all, delete-orphan")


class Score(Base, TimestampMixin):
    __tablename__ = "scores"

    score_run_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("score_runs.id", ondelete="CASCADE"), nullable=False, index=True)
    kind: Mapped[str] = mapped_column(String(50), nullable=False, index=True) # pps, tss, ntss, jrs, career_match
    target_role_slug: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    value: Mapped[float] = mapped_column(Float, nullable=False) # 0 to 100
    band: Mapped[str] = mapped_column(String(50), nullable=False) # emerging, developing, solid, strong, exceptional
    confidence: Mapped[float] = mapped_column(Float, nullable=False) # 0 to 1
    delta_since_last: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    explanation: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    score_run: Mapped["ScoreRun"] = relationship("ScoreRun", back_populates="scores")


class DnaProfile(Base, TimestampMixin):
    __tablename__ = "dna_profiles"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    score_run_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("score_runs.id", ondelete="CASCADE"), nullable=False)
    dimensions: Mapped[Dict[str, float]] = mapped_column(JSON, default=dict, nullable=False)
    archetype_weights: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list, nullable=False)
    narrative: Mapped[Optional[str]] = mapped_column(String(4000), nullable=True)
