"""beacon demonstration schema

Adds the Beacon coastal-storm-readiness demonstration tables: one seeded
workflow definition, idempotent workflow runs, append-only step events,
fixture provenance, and human-reviewed allocation proposals. All data stored
in these tables is synthetic demonstration data.

Revision ID: 0002
Revises: 0001
Create Date: 2026-09-02 00:00:00.000000

"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0002"
down_revision: str | None = "0001"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None

_RUN_STATUS = (
    "received",
    "running",
    "awaiting_approval",
    "approved",
    "completed",
    "rejected",
    "failed",
    "dead_letter",
)
_STEP_STATUS = ("succeeded", "failed", "timed_out", "skipped")
_PROPOSAL_STATUS = ("proposed", "approved", "rejected")


def upgrade() -> None:
    op.create_table(
        "beacon_workflow_definitions",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("key", sa.String(length=100), nullable=False),
        sa.Column("version", sa.String(length=20), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("policy_version", sa.String(length=50), nullable=False),
        sa.Column("steps", sa.JSON(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_beacon_workflow_definitions_key"),
        "beacon_workflow_definitions",
        ["key"],
        unique=True,
    )

    op.create_table(
        "beacon_workflow_runs",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("workflow_key", sa.String(length=100), nullable=False),
        sa.Column("workflow_version", sa.String(length=20), nullable=False),
        sa.Column("policy_version", sa.String(length=50), nullable=False),
        sa.Column("organization_id", sa.String(length=36), nullable=False),
        sa.Column("created_by_user_id", sa.String(length=36), nullable=False),
        sa.Column("idempotency_key", sa.String(length=100), nullable=False),
        sa.Column("scenario", sa.String(length=50), nullable=False),
        sa.Column("fixture_id", sa.String(length=100), nullable=False),
        sa.Column(
            "status",
            sa.Enum(*_RUN_STATUS, name="beaconrunstatus", native_enum=False, length=30),
            nullable=False,
        ),
        sa.Column("policy_results", sa.JSON(), nullable=False),
        sa.Column("metrics", sa.JSON(), nullable=False),
        sa.Column("disclosures", sa.JSON(), nullable=False),
        sa.Column("replay_count", sa.Integer(), nullable=False),
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
        sa.ForeignKeyConstraint(
            ["organization_id"], ["organizations.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "organization_id", "idempotency_key", name="uq_beacon_run_org_idempotency"
        ),
    )

    op.create_table(
        "beacon_workflow_run_steps",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("run_id", sa.String(length=36), nullable=False),
        sa.Column("seq", sa.Integer(), nullable=False),
        sa.Column("step_key", sa.String(length=100), nullable=False),
        sa.Column("tool_name", sa.String(length=100), nullable=False),
        sa.Column("attempt", sa.Integer(), nullable=False),
        sa.Column(
            "status",
            sa.Enum(*_STEP_STATUS, name="beaconstepstatus", native_enum=False, length=30),
            nullable=False,
        ),
        sa.Column("detail", sa.JSON(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["run_id"], ["beacon_workflow_runs.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "beacon_fixture_provenance",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("run_id", sa.String(length=36), nullable=False),
        sa.Column("fixture_id", sa.String(length=100), nullable=False),
        sa.Column("source_label", sa.String(length=200), nullable=False),
        sa.Column("synthetic", sa.Boolean(), nullable=False),
        sa.Column("license_note", sa.String(length=300), nullable=False),
        sa.Column("checksum_sha256", sa.String(length=64), nullable=False),
        sa.Column("effective_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("retrieved_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["run_id"], ["beacon_workflow_runs.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "beacon_allocation_proposals",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("run_id", sa.String(length=36), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                *_PROPOSAL_STATUS, name="beaconproposalstatus", native_enum=False, length=30
            ),
            nullable=False,
        ),
        sa.Column("lines", sa.JSON(), nullable=False),
        sa.Column("unmet_demand", sa.JSON(), nullable=False),
        sa.Column("decided_by_user_id", sa.String(length=36), nullable=True),
        sa.Column("decided_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("decision_note", sa.String(length=500), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["run_id"], ["beacon_workflow_runs.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["decided_by_user_id"], ["users.id"], ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("run_id"),
    )


def downgrade() -> None:
    op.drop_table("beacon_allocation_proposals")
    op.drop_table("beacon_fixture_provenance")
    op.drop_table("beacon_workflow_run_steps")
    op.drop_table("beacon_workflow_runs")
    op.drop_index(
        op.f("ix_beacon_workflow_definitions_key"),
        table_name="beacon_workflow_definitions",
    )
    op.drop_table("beacon_workflow_definitions")
