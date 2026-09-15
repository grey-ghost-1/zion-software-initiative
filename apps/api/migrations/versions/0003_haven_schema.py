"""haven schema

Adds the Haven demonstration tables: curated plain-language guidance cards,
curated outbound resources with provenance/freshness metadata, and synthetic
organization-scoped navigation plans that store only controlled enum values
and boolean safety flags (never free text, identity, or location).

Revision ID: 0003
Revises: 0002
Create Date: 2026-09-02 00:00:00.000000

"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0003"
down_revision: str | None = "0002"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None

_CONCERN_CATEGORY = (
    "fever_or_flu",
    "cough_or_cold",
    "stomach_trouble",
    "minor_injury",
    "medication_instructions",
    "stress_or_anxiety",
    "low_mood",
    "sleep_trouble",
    "cost_or_coverage",
    "general_question",
)
_CONCERN_DURATION = (
    "under_one_day",
    "one_to_three_days",
    "four_to_seven_days",
    "over_one_week",
)
_SEVERITY = ("mild", "moderate", "severe")
_ROUTING_OUTCOME = (
    "emergency_now",
    "crisis_support_now",
    "clinician_soon",
    "mental_health_support",
    "low_cost_care_routing",
    "self_care_education",
)
_PLAN_STATUS = ("open", "reviewed", "closed")
_REVIEW_REASON_CODE = (
    "routing_confirmed",
    "routing_too_cautious",
    "routing_not_cautious_enough",
    "resource_link_problem",
    "demo_walkthrough_complete",
)
_RESOURCE_KIND = ("crisis_support", "treatment_locator", "low_cost_care", "health_education")
_SOURCE_MODE = ("live_official", "synthetic_demo")
_PROVENANCE = ("federal_agency", "nonprofit_official", "synthetic")


def _enum(values: tuple[str, ...], name: str) -> sa.Enum:
    return sa.Enum(*values, name=name, native_enum=False, length=40)


def upgrade() -> None:
    op.create_table(
        "haven_resources",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("slug", sa.String(length=100), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("description", sa.String(length=500), nullable=False),
        sa.Column("url", sa.String(length=500), nullable=False),
        sa.Column("kind", _enum(_RESOURCE_KIND, "haven_resource_kind"), nullable=False),
        sa.Column("jurisdiction", sa.String(length=50), nullable=False),
        sa.Column("provenance", _enum(_PROVENANCE, "haven_provenance"), nullable=False),
        sa.Column("source_mode", _enum(_SOURCE_MODE, "haven_source_mode"), nullable=False),
        sa.Column("reviewed_on", sa.Date(), nullable=False),
        sa.Column("retrieved_on", sa.Date(), nullable=False),
        sa.Column("review_valid_until", sa.Date(), nullable=False),
        sa.Column("is_available", sa.Boolean(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_haven_resources_slug"), "haven_resources", ["slug"], unique=True)

    op.create_table(
        "haven_guidance_cards",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("slug", sa.String(length=100), nullable=False),
        sa.Column(
            "category", _enum(_CONCERN_CATEGORY, "haven_concern_category"), nullable=False
        ),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("original_text", sa.String(length=1000), nullable=False),
        sa.Column("plain_text", sa.String(length=1000), nullable=False),
        sa.Column("source_name", sa.String(length=200), nullable=False),
        sa.Column("source_url", sa.String(length=500), nullable=False),
        sa.Column("jurisdiction", sa.String(length=50), nullable=False),
        sa.Column("reviewed_on", sa.Date(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_haven_guidance_cards_slug"), "haven_guidance_cards", ["slug"], unique=True
    )

    op.create_table(
        "haven_navigation_plans",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("organization_id", sa.String(length=36), nullable=False),
        sa.Column("created_by_user_id", sa.String(length=36), nullable=False),
        sa.Column("synthetic", sa.Boolean(), nullable=False),
        sa.Column(
            "concern_category",
            _enum(_CONCERN_CATEGORY, "haven_concern_category"),
            nullable=False,
        ),
        sa.Column("duration", _enum(_CONCERN_DURATION, "haven_concern_duration"), nullable=False),
        sa.Column("severity", _enum(_SEVERITY, "haven_severity"), nullable=False),
        sa.Column("immediate_danger", sa.Boolean(), nullable=False),
        sa.Column("self_harm_risk", sa.Boolean(), nullable=False),
        sa.Column("crisis_language_detected", sa.Boolean(), nullable=False),
        sa.Column(
            "routed_outcome", _enum(_ROUTING_OUTCOME, "haven_routing_outcome"), nullable=False
        ),
        sa.Column("status", _enum(_PLAN_STATUS, "haven_plan_status"), nullable=False),
        sa.Column(
            "review_reason_code",
            _enum(_REVIEW_REASON_CODE, "haven_review_reason_code"),
            nullable=True,
        ),
        sa.Column("reviewed_by_user_id", sa.String(length=36), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["reviewed_by_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_haven_navigation_plans_organization_id"),
        "haven_navigation_plans",
        ["organization_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_haven_navigation_plans_organization_id"), table_name="haven_navigation_plans"
    )
    op.drop_table("haven_navigation_plans")
    op.drop_index(op.f("ix_haven_guidance_cards_slug"), table_name="haven_guidance_cards")
    op.drop_table("haven_guidance_cards")
    op.drop_index(op.f("ix_haven_resources_slug"), table_name="haven_resources")
    op.drop_table("haven_resources")
