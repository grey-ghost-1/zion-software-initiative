"""Alembic migration tests: upgrade/downgrade correctness against a real DB.

These run against a temporary SQLite file rather than Postgres so CI does not
need a live database service; the migration itself is dialect-agnostic except
for the Postgres-only immutability trigger, which is skipped automatically on
SQLite (see migrations/versions/0001_initial_schema.py).
"""

from __future__ import annotations

import os
import uuid
from pathlib import Path

from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory
from sqlalchemy import create_engine, inspect

API_ROOT = Path(__file__).resolve().parents[1]

EXPECTED_TABLES = {
    "organizations",
    "users",
    "auth_tokens",
    "memberships",
    "audit_events",
    "haven_resources",
    "haven_guidance_cards",
    "haven_navigation_plans",
    "harbor_capacities",
    "harbor_needs",
    "harbor_plans",
    "harbor_resources",
    "harbor_volunteer_availability",
    "alembic_version",
}

EXPECTED_REVISIONS = ["0003", "0002", "0001"]


def _alembic_config(database_url: str) -> Config:
    config = Config(str(API_ROOT / "alembic.ini"))
    config.set_main_option("script_location", str(API_ROOT / "migrations"))
    os.environ["ZION_DATABASE_URL"] = database_url
    return config


def test_upgrade_head_creates_the_expected_tables(tmp_path: Path) -> None:
    db_path = tmp_path / f"{uuid.uuid4().hex}.db"
    database_url = f"sqlite:///{db_path}"
    config = _alembic_config(database_url)

    command.upgrade(config, "head")

    engine = create_engine(database_url)
    tables = set(inspect(engine).get_table_names())
    assert tables == EXPECTED_TABLES
    engine.dispose()


def test_migration_history_has_one_linear_head() -> None:
    scripts = ScriptDirectory.from_config(_alembic_config("sqlite://"))

    assert scripts.get_heads() == ["0003"]
    assert [revision.revision for revision in scripts.walk_revisions()] == EXPECTED_REVISIONS


def test_downgrade_base_removes_every_table(tmp_path: Path) -> None:
    db_path = tmp_path / f"{uuid.uuid4().hex}.db"
    database_url = f"sqlite:///{db_path}"
    config = _alembic_config(database_url)

    command.upgrade(config, "head")
    command.downgrade(config, "base")

    engine = create_engine(database_url)
    tables = set(inspect(engine).get_table_names())
    assert tables.isdisjoint(EXPECTED_TABLES - {"alembic_version"})
    engine.dispose()


def test_upgrade_head_is_idempotent_when_rerun(tmp_path: Path) -> None:
    db_path = tmp_path / f"{uuid.uuid4().hex}.db"
    database_url = f"sqlite:///{db_path}"
    config = _alembic_config(database_url)

    command.upgrade(config, "head")
    command.upgrade(config, "head")  # must not raise or duplicate schema objects

    engine = create_engine(database_url)
    tables = set(inspect(engine).get_table_names())
    assert tables == EXPECTED_TABLES
    engine.dispose()
