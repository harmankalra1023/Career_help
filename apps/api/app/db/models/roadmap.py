import uuid
from typing import Optional, Dict, Any, List
from sqlalchemy import String, Integer, Float, Boolean, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, TimestampMixin


class Roadmap(Base, TimestampMixin):
    __tablename__ = "roadmaps"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    target_role_slug: Mapped[str] = mapped_column(String(100), nullable=False)
    horizon_months: Mapped[int] = mapped_column(Integer, default=6, nullable=False)
    weekly_hours: Mapped[float] = mapped_column(Float, default=8.0, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="active", nullable=False)
    params_json: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    milestones: Mapped[List["Milestone"]] = relationship("Milestone", back_populates="roadmap", cascade="all, delete-orphan")


class Milestone(Base, TimestampMixin):
    __tablename__ = "milestones"

    roadmap_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("roadmaps.id", ondelete="CASCADE"), nullable=False, index=True)
    sequence_order: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    phase: Mapped[str] = mapped_column(String(50), nullable=False) # Foundation, Core, Applied, etc.
    month_index: Mapped[int] = mapped_column(Integer, nullable=False)
    estimated_hours: Mapped[float] = mapped_column(Float, nullable=False)
    is_locked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="todo", nullable=False)
    skills: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    resources: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list, nullable=False)

    roadmap: Mapped["Roadmap"] = relationship("Roadmap", back_populates="milestones")
