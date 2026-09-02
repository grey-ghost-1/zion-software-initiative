"""Harbor synthetic coordination schema

Revision ID: 0003
Revises: 0002
Create Date: 2026-09-01 23:15:00.000000
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0003"
down_revision: str | None = "0002"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def _enum(*values: str, name: str, length: int) -> sa.Enum:
    return sa.Enum(*values, name=name, native_enum=False, length=length)


def upgrade() -> None:
    op.create_table(
        "harbor_resources",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("organization_id", sa.String(length=36), nullable=False),
        sa.Column("code", sa.String(length=32), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column(
            "category",
            _enum(
                "food",
                "temporary_shelter",
                "essential_supplies",
                "transportation",
                name="needcategory",
                length=32,
            ),
            nullable=False,
        ),
        sa.Column(
            "zone", _enum("north", "central", "south", name="harborzone", length=16), nullable=False
        ),
        sa.Column(
            "eligibility",
            _enum(
                "open_access",
                "coordinator_referral",
                name="eligibility",
                length=32,
            ),
            nullable=False,
        ),
        sa.Column(
            "accessibility",
            _enum("step_free", "limited", "unknown", name="accessibilitystatus", length=16),
            nullable=False,
        ),
        sa.Column(
            "status",
            _enum("open", "closed", name="resourcestatus", length=16),
            nullable=False,
        ),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("organization_id", "code", name="uq_harbor_resource_org_code"),
    )
    op.create_index(
        op.f("ix_harbor_resources_organization_id"),
        "harbor_resources",
        ["organization_id"],
        unique=False,
    )

    op.create_table(
        "harbor_needs",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("organization_id", sa.String(length=36), nullable=False),
        sa.Column("request_ref", sa.String(length=32), nullable=False),
        sa.Column(
            "category",
            _enum(
                "food",
                "temporary_shelter",
                "essential_supplies",
                "transportation",
                name="needcategory",
                length=32,
            ),
            nullable=False,
        ),
        sa.Column(
            "zone", _enum("north", "central", "south", name="harborzone", length=16), nullable=False
        ),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column(
            "eligibility",
            _enum(
                "open_access",
                "coordinator_referral",
                name="eligibility",
                length=32,
            ),
            nullable=False,
        ),
        sa.Column(
            "accessibility_requirement",
            _enum("none", "step_free", name="accessibilityrequirement", length=16),
            nullable=False,
        ),
        sa.Column(
            "urgency",
            _enum("standard", "time_sensitive", name="needurgency", length=24),
            nullable=False,
        ),
        sa.Column(
            "status",
            _enum(
                "submitted",
                "triaged",
                "deferred",
                "proposed",
                "approved",
                "fulfilled",
                name="needstatus",
                length=16,
            ),
            nullable=False,
        ),
        sa.Column(
            "triage_decision",
            _enum("ready", "defer", name="triagedecision", length=16),
            nullable=True,
        ),
        sa.Column(
            "triage_reason",
            _enum(
                "match_explanation_reviewed",
                "capacity_recheck_required",
                "synthetic_scenario_hold",
                "coordinator_override",
                name="triagereason",
                length=40,
            ),
            nullable=True,
        ),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.CheckConstraint("quantity BETWEEN 1 AND 8", name="ck_harbor_need_quantity"),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("organization_id", "request_ref", name="uq_harbor_need_org_ref"),
    )
    op.create_index(
        op.f("ix_harbor_needs_organization_id"),
        "harbor_needs",
        ["organization_id"],
        unique=False,
    )

    op.create_table(
        "harbor_capacities",
        sa.Column("resource_id", sa.String(length=36), nullable=False),
        sa.Column("organization_id", sa.String(length=36), nullable=False),
        sa.Column("total_units", sa.Integer(), nullable=False),
        sa.Column("reserved_units", sa.Integer(), nullable=False),
        sa.Column("fulfilled_units", sa.Integer(), nullable=False),
        sa.Column(
            "freshness",
            _enum("current", "stale", "unknown", name="capacityfreshness", length=16),
            nullable=False,
        ),
        sa.Column("observed_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("total_units >= 0", name="ck_harbor_capacity_total"),
        sa.CheckConstraint("reserved_units >= 0", name="ck_harbor_capacity_reserved"),
        sa.CheckConstraint("fulfilled_units >= 0", name="ck_harbor_capacity_fulfilled"),
        sa.CheckConstraint(
            "reserved_units + fulfilled_units <= total_units",
            name="ck_harbor_capacity_not_overbooked",
        ),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["resource_id"], ["harbor_resources.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("resource_id"),
    )
    op.create_index(
        op.f("ix_harbor_capacities_organization_id"),
        "harbor_capacities",
        ["organization_id"],
        unique=False,
    )

    op.create_table(
        "harbor_volunteer_availability",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("organization_id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("code", sa.String(length=32), nullable=False),
        sa.Column(
            "zone", _enum("north", "central", "south", name="harborzone", length=16), nullable=False
        ),
        sa.Column(
            "category",
            _enum(
                "food",
                "temporary_shelter",
                "essential_supplies",
                "transportation",
                name="needcategory",
                length=32,
            ),
            nullable=False,
        ),
        sa.Column("available", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("organization_id", "code", name="uq_harbor_volunteer_org_code"),
    )
    op.create_index(
        op.f("ix_harbor_volunteer_availability_organization_id"),
        "harbor_volunteer_availability",
        ["organization_id"],
        unique=False,
    )

    op.create_table(
        "harbor_plans",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("organization_id", sa.String(length=36), nullable=False),
        sa.Column("need_id", sa.String(length=36), nullable=False),
        sa.Column("resource_id", sa.String(length=36), nullable=False),
        sa.Column("volunteer_availability_id", sa.String(length=36), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column(
            "status",
            _enum("proposed", "approved", "fulfilled", name="planstatus", length=16),
            nullable=False,
        ),
        sa.Column(
            "proposed_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("fulfilled_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("quantity BETWEEN 1 AND 8", name="ck_harbor_plan_quantity"),
        sa.ForeignKeyConstraint(["need_id"], ["harbor_needs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["resource_id"], ["harbor_resources.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(
            ["volunteer_availability_id"],
            ["harbor_volunteer_availability.id"],
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("organization_id", "need_id", name="uq_harbor_plan_org_need"),
    )
    op.create_index(
        op.f("ix_harbor_plans_organization_id"),
        "harbor_plans",
        ["organization_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_harbor_plans_organization_id"), table_name="harbor_plans")
    op.drop_table("harbor_plans")
    op.drop_index(
        op.f("ix_harbor_volunteer_availability_organization_id"),
        table_name="harbor_volunteer_availability",
    )
    op.drop_table("harbor_volunteer_availability")
    op.drop_index(
        op.f("ix_harbor_capacities_organization_id"), table_name="harbor_capacities"
    )
    op.drop_table("harbor_capacities")
    op.drop_index(op.f("ix_harbor_needs_organization_id"), table_name="harbor_needs")
    op.drop_table("harbor_needs")
    op.drop_index(
        op.f("ix_harbor_resources_organization_id"), table_name="harbor_resources"
    )
    op.drop_table("harbor_resources")
