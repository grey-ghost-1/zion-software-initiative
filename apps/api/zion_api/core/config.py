"""Environment-driven configuration for the Zion API.

Settings are read once per process from environment variables (prefixed with
``ZION_``) and an optional ``.env`` file. No secret defaults are committed;
the Docker Compose Postgres credentials in ``.env.example`` are synthetic
local-development values only.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Strongly typed application settings."""

    model_config = SettingsConfigDict(
        env_prefix="ZION_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    environment: Literal["development", "test", "production"] = "development"

    database_url: str = "postgresql+psycopg://zion:zion@localhost:5432/zion"

    cors_allowed_origins: list[str] = ["http://localhost:3000"]

    session_token_ttl_minutes: int = 12 * 60

    log_level: str = "INFO"


@lru_cache
def get_settings() -> Settings:
    """Return the process-wide settings singleton."""

    return Settings()
