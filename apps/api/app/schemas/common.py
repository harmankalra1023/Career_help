from datetime import datetime, timezone
from typing import Any, List, Optional
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = "ok"
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    version: str = "0.1.0"


class ReadyResponse(BaseModel):
    status: str
    database: bool
    redis: bool
    migrations_at_head: bool


class ErrorDetail(BaseModel):
    field: Optional[str] = None
    message: str


class ProblemDetail(BaseModel):
    type: str = "about:blank"
    title: str
    status: int
    detail: Optional[str] = None
    errors: Optional[List[ErrorDetail]] = None
