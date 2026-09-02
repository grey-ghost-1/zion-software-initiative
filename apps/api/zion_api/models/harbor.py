"""Harbor's bounded synthetic coordination models."""

from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from zion_api.db.base import Base


def _enum(enum_type: type[enum.StrEnum], length: int) -> Enum:
    return Enum(
        enum_type,
        native_enum=False,
        validate_strings=True,
        length=length,
        values_callable=lambda values: [member.value for member in values],
    )


class NeedCategory(enum.StrEnum):
    FOOD = "food"
    TEMPORARY_SHELTER = "temporary_shelter"
    ESSENTIAL_SUPPLIES = "essential_supplies"
    TRANSPORTATION = "transportation"


class HarborZone(enum.StrEnum):
    NORTH = "north"
    CENTRAL = "central"
    SOUTH = "south"


class Eligibility(enum.StrEnum):
    OPEN_ACCESS = "open_access"
    COORDINATOR_REFERRAL = "coordinator_referral"


class AccessibilityRequirement(enum.StrEnum):
    NONE = "none"
    STEP_FREE = "step_free"


class AccessibilityStatus(enum.StrEnum):
    STEP_FREE = "step_free"
    LIMITED = "limited"
    UNKNOWN = "unknown"


class ResourceStatus(enum.StrEnum):
    OPEN = "open"
    CLOSED = "closed"


class CapacityFreshness(enum.StrEnum):
    CURRENT = "current"
    STALE = "stale"
    UNKNOWN = "unknown"


class NeedUrgency(enum.StrEnum):
    STANDARD = "standard"
    TIME_SENSITIVE = "time_sensitive"


class NeedStatus(enum.StrEnum):
    SUBMITTED = "submitted"
    TRIAGED = "triaged"
    DEFERRED = "deferred"
    PROPOSED = "proposed"
    APPROVED = "approved"
    FULFILLED = "fulfilled"


class TriageDecision(enum.StrEnum):
    READY = "ready"
    DEFER = "defer"


class TriageReason(enum.StrEnum):
    MATCH_EXPLANATION_REVIEWED = "match_explanation_reviewed"
    CAPACITY_RECHECK_REQUIRED = "capacity_recheck_required"
    SYNTHETIC_SCENARIO_HOLD = "synthetic_scenario_hold"
    COORDINATOR_OVERRIDE = "coordinator_override"


class PlanStatus(enum.StrEnum):
    PROPOSED = "proposed"
    APPROVED = "approved"
    FULFILLED = "fulfilled"


class HarborResource(Base):
    __tablename__ = "harbor_resources"
    __table_args__ = (
        UniqueConstraint("organization_id", "code", name="uq_harbor_resource_org_code"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    code: Mapped[str] = mapped_column(String(32), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    category: Mapped[NeedCategory] = mapped_column(_enum(NeedCategory, 32), nullable=False)
    zone: Mapped[HarborZone] = mapped_column(_enum(HarborZone, 16), nullable=False)
    eligibility: Mapped[Eligibility] = mapped_column(_enum(Eligibility, 32), nullable=False)
    accessibility: Mapped[AccessibilityStatus] = mapped_column(
        _enum(AccessibilityStatus, 16), nullable=False
    )
    status: Mapped[ResourceStatus] = mapped_column(_enum(ResourceStatus, 16), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class HarborNeed(Base):
    __tablename__ = "harbor_needs"
    __table_args__ = (
        UniqueConstraint("organization_id", "request_ref", name="uq_harbor_need_org_ref"),
        CheckConstraint("quantity BETWEEN 1 AND 8", name="ck_harbor_need_quantity"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    request_ref: Mapped[str] = mapped_column(String(32), nullable=False)
    category: Mapped[NeedCategory] = mapped_column(_enum(NeedCategory, 32), nullable=False)
    zone: Mapped[HarborZone] = mapped_column(_enum(HarborZone, 16), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    eligibility: Mapped[Eligibility] = mapped_column(_enum(Eligibility, 32), nullable=False)
    accessibility_requirement: Mapped[AccessibilityRequirement] = mapped_column(
        _enum(AccessibilityRequirement, 16), nullable=False
    )
    urgency: Mapped[NeedUrgency] = mapped_column(_enum(NeedUrgency, 24), nullable=False)
    status: Mapped[NeedStatus] = mapped_column(
        _enum(NeedStatus, 16), nullable=False, default=NeedStatus.SUBMITTED
    )
    triage_decision: Mapped[TriageDecision | None] = mapped_column(
        _enum(TriageDecision, 16), nullable=True
    )
    triage_reason: Mapped[TriageReason | None] = mapped_column(
        _enum(TriageReason, 40), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )


class HarborCapacity(Base):
    __tablename__ = "harbor_capacities"
    __table_args__ = (
        CheckConstraint("total_units >= 0", name="ck_harbor_capacity_total"),
        CheckConstraint("reserved_units >= 0", name="ck_harbor_capacity_reserved"),
        CheckConstraint("fulfilled_units >= 0", name="ck_harbor_capacity_fulfilled"),
        CheckConstraint(
            "reserved_units + fulfilled_units <= total_units",
            name="ck_harbor_capacity_not_overbooked",
        ),
    )

    resource_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("harbor_resources.id", ondelete="CASCADE"),
        primary_key=True,
    )
    organization_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    total_units: Mapped[int] = mapped_column(Integer, nullable=False)
    reserved_units: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    fulfilled_units: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    freshness: Mapped[CapacityFreshness] = mapped_column(
        _enum(CapacityFreshness, 16), nullable=False
    )
    observed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class HarborVolunteerAvailability(Base):
    __tablename__ = "harbor_volunteer_availability"
    __table_args__ = (
        UniqueConstraint("organization_id", "code", name="uq_harbor_volunteer_org_code"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    code: Mapped[str] = mapped_column(String(32), nullable=False)
    zone: Mapped[HarborZone] = mapped_column(_enum(HarborZone, 16), nullable=False)
    category: Mapped[NeedCategory] = mapped_column(_enum(NeedCategory, 32), nullable=False)
    available: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class HarborPlan(Base):
    __tablename__ = "harbor_plans"
    __table_args__ = (
        UniqueConstraint("organization_id", "need_id", name="uq_harbor_plan_org_need"),
        CheckConstraint("quantity BETWEEN 1 AND 8", name="ck_harbor_plan_quantity"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    need_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("harbor_needs.id", ondelete="CASCADE"), nullable=False
    )
    resource_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("harbor_resources.id", ondelete="RESTRICT"), nullable=False
    )
    volunteer_availability_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("harbor_volunteer_availability.id", ondelete="RESTRICT"),
        nullable=False,
    )
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[PlanStatus] = mapped_column(
        _enum(PlanStatus, 16), nullable=False, default=PlanStatus.PROPOSED
    )
    proposed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    fulfilled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
