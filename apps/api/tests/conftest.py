import sys
from collections.abc import Iterator
from pathlib import Path

API_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(API_ROOT))

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import Session, sessionmaker  # noqa: E402
from sqlalchemy.pool import StaticPool  # noqa: E402

from zion_api import models  # noqa: E402,F401  (registers all model metadata)
from zion_api.db.base import Base  # noqa: E402
from zion_api.db.session import get_db  # noqa: E402
from zion_api.main import app  # noqa: E402
from zion_api.seed import DEMO_PASSWORD, seed_demo_data  # noqa: E402

__all__ = ["DEMO_PASSWORD"]


@pytest.fixture
def db_session() -> Iterator[Session]:
    """An isolated, fully migrated-shape in-memory database per test."""

    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(
        bind=engine, autoflush=False, autocommit=False, expire_on_commit=False
    )
    session = session_factory()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


@pytest.fixture
def seeded_db_session(db_session: Session) -> Session:
    """A database session pre-populated with deterministic demo data."""

    seed_demo_data(db_session)
    db_session.commit()
    return db_session


@pytest.fixture
def client(db_session: Session) -> Iterator[TestClient]:
    """A TestClient wired to the isolated per-test database session."""

    def override_get_db() -> Iterator[Session]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.pop(get_db, None)


@pytest.fixture
def seeded_client(seeded_db_session: Session, client: TestClient) -> TestClient:
    """A TestClient backed by a database already populated with demo data."""

    return client

