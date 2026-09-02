"""Haven models: curated guidance/resource cards and synthetic navigation plans.

Haven is a non-diagnostic health-access navigation demonstration. These tables
deliberately cannot hold sensitive personal or health data:

- Free-text concern input is **never** persisted; navigation plans store only
  controlled enumeration values and boolean safety flags.
- There are no columns for identity, location, date of birth, medical records,
  diagnoses, medications, or any narrative history.
- Every plan row is marked ``synthetic`` so demo state can never be mistaken
  for real patient data.
"""

from __future__ import annotations

import enum
import uuid
from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, Enum, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from zion_api.db.base import Base


class HavenConcernCategory(enum.StrEnum):
    """Controlled vocabulary for the kind of concern a demo scenario explores."""

    FEVER_OR_FLU = "fever_or_flu"
    COUGH_OR_COLD = "cough_or_cold"
    STOMACH_TROUBLE = "stomach_trouble"
    MINOR_INJURY = "minor_injury"
    MEDICATION_INSTRUCTIONS = "medication_instructions"
    STRESS_OR_ANXIETY = "stress_or_anxiety"
    LOW_MOOD = "low_mood"
    SLEEP_TROUBLE = "sleep_trouble"
    COST_OR_COVERAGE = "cost_or_coverage"
    GENERAL_QUESTION = "general_question"


class HavenConcernDuration(enum.StrEnum):
    UNDER_ONE_DAY = "under_one_day"
    ONE_TO_THREE_DAYS = "one_to_three_days"
    FOUR_TO_SEVEN_DAYS = "four_to_seven_days"
    OVER_ONE_WEEK = "over_one_week"


class HavenSeverity(enum.StrEnum):
    """Self-described impact on daily activities — never a clinical rating."""

    MILD = "mild"
    MODERATE = "moderate"
    SEVERE = "severe"


class HavenRoutingOutcome(enum.StrEnum):
    """Deterministic, non-diagnostic navigation outcomes."""

    EMERGENCY_NOW = "emergency_now"
    CRISIS_SUPPORT_NOW = "crisis_support_now"
    CLINICIAN_SOON = "clinician_soon"
    MENTAL_HEALTH_SUPPORT = "mental_health_support"
    LOW_COST_CARE_ROUTING = "low_cost_care_routing"
    SELF_CARE_EDUCATION = "self_care_education"


class HavenPlanStatus(enum.StrEnum):
    OPEN = "open"
    REVIEWED = "reviewed"
    CLOSED = "closed"


class HavenReviewReasonCode(enum.StrEnum):
    """Controlled reason codes for navigator review — no free-text annotation."""

    ROUTING_CONFIRMED = "routing_confirmed"
    ROUTING_TOO_CAUTIOUS = "routing_too_cautious"
    ROUTING_NOT_CAUTIOUS_ENOUGH = "routing_not_cautious_enough"
    RESOURCE_LINK_PROBLEM = "resource_link_problem"
    DEMO_WALKTHROUGH_COMPLETE = "demo_walkthrough_complete"


class HavenResourceKind(enum.StrEnum):
    CRISIS_SUPPORT = "crisis_support"
    TREATMENT_LOCATOR = "treatment_locator"
    LOW_COST_CARE = "low_cost_care"
    HEALTH_EDUCATION = "health_education"


class HavenSourceMode(enum.StrEnum):
    """Whether an entry references a real official service or synthetic demo data."""

    LIVE_OFFICIAL = "live_official"
    SYNTHETIC_DEMO = "synthetic_demo"


class HavenProvenance(enum.StrEnum):
    FEDERAL_AGENCY = "federal_agency"
    NONPROFIT_OFFICIAL = "nonprofit_official"
    SYNTHETIC = "synthetic"


def _enum_column(enum_cls: type[enum.StrEnum], name: str) -> Enum:
    return Enum(
        enum_cls,
        name=name,
        native_enum=False,
        validate_strings=True,
        length=40,
        values_callable=lambda cls: [member.value for member in cls],
    )


class HavenResource(Base):
    """One curated outbound reference with full provenance. Never fetched at runtime."""

    __tablename__ = "haven_resources"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    kind: Mapped[HavenResourceKind] = mapped_column(
        _enum_column(HavenResourceKind, "haven_resource_kind"), nullable=False
    )
    jurisdiction: Mapped[str] = mapped_column(String(50), nullable=False, default="US")
    provenance: Mapped[HavenProvenance] = mapped_column(
        _enum_column(HavenProvenance, "haven_provenance"), nullable=False
    )
    source_mode: Mapped[HavenSourceMode] = mapped_column(
        _enum_column(HavenSourceMode, "haven_source_mode"), nullable=False
    )
    reviewed_on: Mapped[date] = mapped_column(Date, nullable=False)
    retrieved_on: Mapped[date] = mapped_column(Date, nullable=False)
    review_valid_until: Mapped[date] = mapped_column(Date, nullable=False)
    is_available: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class HavenGuidanceCard(Base):
    """One curated plain-language explanation card (before/after pair).

    Cards are authored and reviewed in the repository, validated for
    number/unit/negation invariance and prohibited content before they are
    served, and never generated at runtime.
    """

    __tablename__ = "haven_guidance_cards"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    category: Mapped[HavenConcernCategory] = mapped_column(
        _enum_column(HavenConcernCategory, "haven_concern_category"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    original_text: Mapped[str] = mapped_column(String(1000), nullable=False)
    plain_text: Mapped[str] = mapped_column(String(1000), nullable=False)
    source_name: Mapped[str] = mapped_column(String(200), nullable=False)
    source_url: Mapped[str] = mapped_column(String(500), nullable=False)
    jurisdiction: Mapped[str] = mapped_column(String(50), nullable=False, default="US")
    reviewed_on: Mapped[date] = mapped_column(Date, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class HavenNavigationPlan(Base):
    """One synthetic, organization-scoped navigation plan.

    Stores only controlled enum values and boolean safety flags. The bounded
    free-text concern a caller may submit is used for the deterministic safety
    check and then discarded — it has no column here by design.
    """

    __tablename__ = "haven_navigation_plans"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    created_by_user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    synthetic: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    concern_category: Mapped[HavenConcernCategory] = mapped_column(
        _enum_column(HavenConcernCategory, "haven_concern_category"), nullable=False
    )
    duration: Mapped[HavenConcernDuration] = mapped_column(
        _enum_column(HavenConcernDuration, "haven_concern_duration"), nullable=False
    )
    severity: Mapped[HavenSeverity] = mapped_column(
        _enum_column(HavenSeverity, "haven_severity"), nullable=False
    )
    immediate_danger: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    self_harm_risk: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    crisis_language_detected: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    routed_outcome: Mapped[HavenRoutingOutcome] = mapped_column(
        _enum_column(HavenRoutingOutcome, "haven_routing_outcome"), nullable=False
    )
    status: Mapped[HavenPlanStatus] = mapped_column(
        _enum_column(HavenPlanStatus, "haven_plan_status"),
        nullable=False,
        default=HavenPlanStatus.OPEN,
    )
    review_reason_code: Mapped[HavenReviewReasonCode | None] = mapped_column(
        _enum_column(HavenReviewReasonCode, "haven_review_reason_code"), nullable=True
    )
    reviewed_by_user_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
