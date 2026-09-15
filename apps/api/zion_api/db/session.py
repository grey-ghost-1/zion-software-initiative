"""Engine/session construction and the FastAPI database dependency.

The engine is created lazily and cached per settings instance, so importing
this module never opens a connection. Connections are only attempted when a
request actually uses the database (for example, on login or the readiness
check), which keeps the app importable and testable without a live database.
"""

from __future__ import annotations

from collections.abc import Generator
from functools import lru_cache

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from zion_api.core.config import Settings, get_settings


@lru_cache
def get_engine(database_url: str) -> Engine:
    """Return a cached engine for the given database URL."""

    connect_args = {"check_same_thread": False} if database_url.startswith("sqlite") else {}
    return create_engine(database_url, pool_pre_ping=True, connect_args=connect_args)


def _session_factory(settings: Settings) -> sessionmaker[Session]:
    engine = get_engine(settings.database_url)
    return sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


def get_db() -> Generator[Session]:
    """FastAPI dependency yielding a request-scoped database session."""

    settings = get_settings()
    session = _session_factory(settings)()
    try:
        yield session
    finally:
        session.close()
