"""Alembic environment configuration.

The database URL always comes from Zion's own :class:`Settings` (environment
variables / ``.env``), never hard-coded in ``alembic.ini``, so migrations use
exactly the same connection the application would use.
"""

from __future__ import annotations

from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from zion_api import models  # noqa: F401  (registers all model metadata)
from zion_api.core.config import Settings
from zion_api.db.base import Base

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def _database_url() -> str:
    # Build settings fresh (never the process-wide ``get_settings()`` cache):
    # migrations run in short-lived, test, and CLI contexts where the
    # environment (e.g. ``ZION_DATABASE_URL``) may change after the app's
    # cached singleton was first populated elsewhere in the same process.
    return Settings().database_url


def run_migrations_offline() -> None:
    """Run migrations without a live DBAPI connection."""

    context.configure(
        url=_database_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations against a live connection."""

    configuration = config.get_section(config.config_ini_section) or {}
    configuration["sqlalchemy.url"] = _database_url()
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
