from typing import Dict, Any, List
from sqlalchemy import String, Float, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base, TimestampMixin


class MarketSnapshot(Base, TimestampMixin):
    __tablename__ = "market_snapshots"

    snapshot_date: Mapped[str] = mapped_column(String(20), index=True, nullable=False)
    region: Mapped[str] = mapped_column(String(50), default="global", nullable=False)
    sources: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    raw_counts: Mapped[Dict[str, int]] = mapped_column(JSON, default=dict, nullable=False)


class MarketRoleMetric(Base, TimestampMixin):
    __tablename__ = "market_role_metrics"

    role_slug: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    region: Mapped[str] = mapped_column(String(50), default="global", nullable=False)
    demand_score: Mapped[float] = mapped_column(Float, nullable=False)
    growth_12m_pct: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    salary_p50: Mapped[float] = mapped_column(Float, nullable=False)
    top_skills: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list, nullable=False)
