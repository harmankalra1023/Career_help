import os
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# Determine database URL:
# For local dev without a running PostgreSQL container, default to SQLite (aiosqlite)
# In Docker compose, DATABASE_URL points to db:5432 (Postgres + pgvector)
raw_url = os.environ.get("DATABASE_URL", settings.DATABASE_URL)

if ("localhost:5432" in raw_url or "127.0.0.1:5432" in raw_url) and os.environ.get("FORCE_POSTGRES", "").lower() != "true":
    logger.info("Local PostgreSQL not detected. Using embedded SQLite (aiosqlite) database.")
    database_url = "sqlite+aiosqlite:///./dct.db"
    connect_args = {"check_same_thread": False}
else:
    database_url = raw_url
    connect_args = {}

engine = create_async_engine(
    database_url,
    echo=(settings.APP_ENV == "development" and settings.LOG_LEVEL == "DEBUG"),
    future=True,
    connect_args=connect_args
)

async_session_factory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)
