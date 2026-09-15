"""ORM models for the shared Zion schema.

Importing this package registers every model (and the audit-immutability
guard) with the shared declarative base, which Alembic's env.py relies on for
autogeneration diffing.
"""

from __future__ import annotations

from zion_api.db import audit_guard as audit_guard  # noqa: F401  (registers event listener)
from zion_api.models.audit_event import AuditEvent
from zion_api.models.auth_token import AuthToken
from zion_api.models.enums import Role
from zion_api.models.harbor import (
    AccessibilityRequirement,
    AccessibilityStatus,
    CapacityFreshness,
    Eligibility,
    HarborCapacity,
    HarborNeed,
    HarborPlan,
    HarborResource,
    HarborVolunteerAvailability,
    HarborZone,
    NeedCategory,
    NeedStatus,
    NeedUrgency,
    PlanStatus,
    ResourceStatus,
    TriageDecision,
    TriageReason,
)
from zion_api.models.haven import (
    HavenGuidanceCard,
    HavenNavigationPlan,
    HavenResource,
)
from zion_api.models.membership import Membership
from zion_api.models.organization import Organization
from zion_api.models.user import User

__all__ = [
    "AuditEvent",
    "AuthToken",
    "AccessibilityRequirement",
    "AccessibilityStatus",
    "CapacityFreshness",
    "Eligibility",
    "HarborCapacity",
    "HarborNeed",
    "HarborPlan",
    "HarborResource",
    "HarborVolunteerAvailability",
    "HarborZone",
    "HavenGuidanceCard",
    "HavenNavigationPlan",
    "HavenResource",
    "Membership",
    "NeedCategory",
    "NeedStatus",
    "NeedUrgency",
    "Organization",
    "Role",
    "PlanStatus",
    "ResourceStatus",
    "TriageDecision",
    "TriageReason",
    "User",
]
