import os
from pathlib import Path
from typing import Any, Dict, Optional
import yaml
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


def find_repo_root() -> Path:
    current = Path(__file__).resolve().parent
    for p in [current, *current.parents]:
        if (p / ".env").exists() or (p / "config").exists() or (p / ".git").exists():
            return p
    return Path.cwd()


REPO_ROOT = find_repo_root()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(str(REPO_ROOT / ".env"), ".env", "../.env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Application
    APP_ENV: str = "development"
    PROJECT_NAME: str = "Digital Career Twin"
    API_V1_STR: str = "/api/v1"
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    LOG_LEVEL: str = "INFO"

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://dct:dct@localhost:5432/dct"
    DATABASE_URL_SYNC: str = "postgresql://dct:dct@localhost:5432/dct"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Security
    JWT_SECRET: str = "dev-secret-key-change-in-production-1234567890"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 14
    ENCRYPTION_KEY: str = "dGhpc2lzYXRlc3RmZXJuZXRrZXkxMjM0NTY3ODkwYWI="

    # LLM & AI Providers
    LLM_PROVIDER: str = "groq" # "groq", "ollama", "openai_compat", "anthropic", "mock"
    LLM_MODEL: str = "llama-3.3-70b-versatile"
    LLM_BASE_URL: str = "https://api.groq.com/openai/v1"
    LLM_API_KEY: Optional[str] = None
    ALLOW_REMOTE_LLM: bool = True

    # Groq specific
    GROQ_API_KEY: Optional[str] = None
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    GROQ_BASE_URL: str = "https://api.groq.com/openai/v1"

    # Embeddings
    EMBED_MODEL: str = "BAAI/bge-small-en-v1.5"
    EMBED_DEVICE: str = "cpu"

    # Storage
    STORAGE_BACKEND: str = "local"
    LOCAL_STORAGE_PATH: str = "./storage"

    # Market
    DEFAULT_REGION: str = "global"
    DEFAULT_CURRENCY: str = "USD"
    MARKET_STALE_DAYS: int = 45


def load_yaml_config(file_name: str) -> Dict[str, Any]:
    config_path = REPO_ROOT / "config" / file_name
    if not config_path.exists():
        # Fallback to relative path if run from different dir
        config_path = Path("config") / file_name
    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    return {}


settings = Settings()
scoring_config = load_yaml_config("scoring.yaml")
archetypes_config = load_yaml_config("archetypes.yaml")
market_config = load_yaml_config("market.yaml")
features_config = load_yaml_config("features.yaml")
