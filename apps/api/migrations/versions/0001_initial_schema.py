"""initial schema

Creates the shared foundation schema: synthetic users, organizations,
memberships (role-based, one row per user per organization), expiring auth
tokens, and an append-only audit_events log.

On PostgreSQL only, this also installs a trigger that rejects any UPDATE or
DELETE on audit_events at the database level, as defense in depth alongside
the SQLAlchemy-level guard in ``zion_api.db.audit_guard`` (which is what
enforces immutability in tests, since tests run against SQLite).

Revision ID: 0001
Revises:
Create Date: 2026-09-01 00:00:00.000000

"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0001"
down_revision: str | None = None
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None

_ROLE_VALUES = ("visitor", "coordinator", "navigator", "volunteer", "admin")

_POSTGRES_IMMUTABILITY_SQL = """
CREATE FUNCTION reject_audit_event_mutation() RETURNS trigger AS $$
BEGIN
    RAISE EXCEPTION 'audit_events is append-only: % is not permitted', TG_OP;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER audit_events_immutable
BEFORE UPDATE OR DELETE ON audit_events
FOR EACH ROW EXECUTE FUNCTION reject_audit_event_mutation();
"""

_POSTGRES_IMMUTABILITY_DROP_SQL = """
DROP TRIGGER IF EXISTS audit_events_immutable ON audit_events;
DROP FUNCTION IF EXISTS reject_audit_event_mutation();
"""


def upgrade() -> None:
    op.create_table(
        "organizations",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("slug", sa.String(length=100), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_organizations_slug"), "organizations", ["slug"], unique=True
    )

    op.create_table(
        "users",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("full_name", sa.String(length=200), nullable=False),
        sa.Column("password_hash", sa.String(length=200), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)

    op.create_table(
        "auth_tokens",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_auth_tokens_token_hash"), "auth_tokens", ["token_hash"], unique=True
    )

    op.create_table(
        "memberships",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("organization_id", sa.String(length=36), nullable=False),
        sa.Column(
            "role",
            sa.Enum(*_ROLE_VALUES, name="role", native_enum=False, length=20),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["organization_id"], ["organizations.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "organization_id", name="uq_membership_user_org"),
    )

    op.create_table(
        "audit_events",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column(
            "occurred_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("action", sa.String(length=100), nullable=False),
        sa.Column("actor_user_id", sa.String(length=36), nullable=True),
        sa.Column("organization_id", sa.String(length=36), nullable=True),
        sa.Column("subject_type", sa.String(length=100), nullable=True),
        sa.Column("subject_id", sa.String(length=100), nullable=True),
        sa.Column("context", sa.JSON(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_audit_events_action"), "audit_events", ["action"], unique=False
    )

    if op.get_bind().dialect.name == "postgresql":
        op.execute(sa.text(_POSTGRES_IMMUTABILITY_SQL))


def downgrade() -> None:
    if op.get_bind().dialect.name == "postgresql":
        op.execute(sa.text(_POSTGRES_IMMUTABILITY_DROP_SQL))

    op.drop_index(op.f("ix_audit_events_action"), table_name="audit_events")
    op.drop_table("audit_events")
    op.drop_table("memberships")
    op.drop_index(op.f("ix_auth_tokens_token_hash"), table_name="auth_tokens")
    op.drop_table("auth_tokens")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")
    op.drop_index(op.f("ix_organizations_slug"), table_name="organizations")
    op.drop_table("organizations")
