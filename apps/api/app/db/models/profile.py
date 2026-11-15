import uuid
from typing import Optional, List
from sqlalchemy import String, Integer, Float, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base, TimestampMixin


class Education(Base, TimestampMixin):
    __tablename__ = "education"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    institution: Mapped[str] = mapped_column(String(255), nullable=False)
    level: Mapped[str] = mapped_column(String(50), nullable=False) # bachelors, masters, etc.
    degree: Mapped[str] = mapped_column(String(255), nullable=False)
    branch: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    start_year: Mapped[int] = mapped_column(Integer, nullable=False)
    end_year: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="completed", nullable=False)
    grade_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    grade_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    grade_normalized: Mapped[Optional[float]] = mapped_column(Float, nullable=True) # 0-100
    relevant_courses: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)


class Experience(Base, TimestampMixin):
    __tablename__ = "experiences"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    company: Mapped[str] = mapped_column(String(255), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    location: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    employment_type: Mapped[str] = mapped_column(String(50), default="full_time", nullable=False)
    start_date: Mapped[str] = mapped_column(String(20), nullable=False)
    end_date: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(String(4000), nullable=True)
    skills_used: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)


class Project(Base, TimestampMixin):
    __tablename__ = "projects"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(String(4000), nullable=False)
    url: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    repo_url: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    skills_used: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    verified: Mapped[bool] = mapped_column(default=False, nullable=False)
