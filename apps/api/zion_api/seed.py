"""Deterministic demo seed data.

Running this module twice must not create duplicates or change identities: it
upserts by natural key (email / slug) and uses stable, name-derived UUIDs so
the same seed always produces the same records.

Usage (from the repository root, after `alembic upgrade head`):

    python -m zion_api.seed

All accounts are synthetic and clearly documented as demo-only. No real
personal, health, or location data is used anywhere in this repository.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import NotRequired, TypedDict

from sqlalchemy.orm import Session

from zion_api.core.security import hash_password
from zion_api.db.session import get_engine
from zion_api.models.enums import Role
from zion_api.models.harbor import (
    AccessibilityRequirement,
    AccessibilityStatus,
    CapacityFreshness,
    Eligibility,
    HarborCapacity,
    HarborNeed,
    HarborResource,
    HarborVolunteerAvailability,
    HarborZone,
    NeedCategory,
    NeedStatus,
    NeedUrgency,
    ResourceStatus,
    TriageDecision,
    TriageReason,
)
from zion_api.models.membership import Membership
from zion_api.models.organization import Organization
from zion_api.models.user import User
from zion_api.services.beacon.engine import ensure_workflow_definition

_NAMESPACE = uuid.UUID("2f9c9c14-9b0c-4e0f-8f0e-8b1a3f7d6c21")

# The synthetic demo password is intentionally published: these are seed-only,
# non-sensitive accounts meant for local exploration and tests, never for
# production use.
DEMO_PASSWORD = "ZionDemo!2026"


def _stable_id(*parts: str) -> str:
    return str(uuid.uuid5(_NAMESPACE, ":".join(parts)))


@dataclass(frozen=True)
class DemoOrganization:
    slug: str
    name: str


@dataclass(frozen=True)
class DemoUser:
    email: str
    full_name: str
    org_slug: str
    role: Role


class HarborResourceSeed(TypedDict):
    code: str
    name: str
    category: NeedCategory
    zone: HarborZone
    eligibility: Eligibility
    accessibility: AccessibilityStatus
    status: ResourceStatus
    capacity: tuple[int, int, int, CapacityFreshness]


class HarborNeedSeed(TypedDict):
    request_ref: str
    category: NeedCategory
    zone: HarborZone
    quantity: int
    eligibility: Eligibility
    accessibility_requirement: AccessibilityRequirement
    urgency: NeedUrgency
    status: NeedStatus
    triage_decision: NotRequired[TriageDecision]
    triage_reason: NotRequired[TriageReason]


DEMO_ORGANIZATIONS = [
    DemoOrganization(slug="zion-demo", name="Zion Demo Cooperative"),
    DemoOrganization(slug="zion-demo-alliance", name="Zion Demo Alliance"),
]

DEMO_USERS = [
    DemoUser("admin@zion.example", "Ari Admin", "zion-demo", Role.ADMIN),
    DemoUser("coordinator@zion.example", "Cam Coordinator", "zion-demo", Role.COORDINATOR),
    DemoUser("navigator@zion.example", "Nia Navigator", "zion-demo", Role.NAVIGATOR),
    DemoUser("volunteer@zion.example", "Val Volunteer", "zion-demo", Role.VOLUNTEER),
    DemoUser("visitor@zion.example", "Vic Visitor", "zion-demo", Role.VISITOR),
    DemoUser(
        "admin@alliance.zion.example", "Alex Alliance-Admin", "zion-demo-alliance", Role.ADMIN
    ),
]

_HARBOR_OBSERVED_AT = datetime(2026, 9, 1, 12, 0, tzinfo=UTC)

HARBOR_RESOURCES: list[HarborResourceSeed] = [
    {
        "code": "RES-NORTH-SHELTER",
        "name": "Synthetic North Harbor Shelter",
        "category": NeedCategory.TEMPORARY_SHELTER,
        "zone": HarborZone.NORTH,
        "eligibility": Eligibility.COORDINATOR_REFERRAL,
        "accessibility": AccessibilityStatus.STEP_FREE,
        "status": ResourceStatus.OPEN,
        "capacity": (8, 2, 1, CapacityFreshness.CURRENT),
    },
    {
        "code": "RES-CENTRAL-PANTRY",
        "name": "Coastal Pantry Demo",
        "category": NeedCategory.FOOD,
        "zone": HarborZone.CENTRAL,
        "eligibility": Eligibility.OPEN_ACCESS,
        "accessibility": AccessibilityStatus.LIMITED,
        "status": ResourceStatus.OPEN,
        "capacity": (20, 2, 3, CapacityFreshness.CURRENT),
    },
    {
        "code": "RES-SOUTH-TRANSIT",
        "name": "South Transit Desk (Synthetic)",
        "category": NeedCategory.TRANSPORTATION,
        "zone": HarborZone.SOUTH,
        "eligibility": Eligibility.OPEN_ACCESS,
        "accessibility": AccessibilityStatus.UNKNOWN,
        "status": ResourceStatus.CLOSED,
        "capacity": (6, 0, 0, CapacityFreshness.CURRENT),
    },
    {
        "code": "RES-CENTRAL-SUPPLIES",
        "name": "Demo Supply Locker",
        "category": NeedCategory.ESSENTIAL_SUPPLIES,
        "zone": HarborZone.CENTRAL,
        "eligibility": Eligibility.OPEN_ACCESS,
        "accessibility": AccessibilityStatus.UNKNOWN,
        "status": ResourceStatus.OPEN,
        "capacity": (12, 0, 0, CapacityFreshness.UNKNOWN),
    },
    {
        "code": "RES-CENTRAL-STALE-BEDS",
        "name": "Old Harbor Beds (Synthetic)",
        "category": NeedCategory.TEMPORARY_SHELTER,
        "zone": HarborZone.CENTRAL,
        "eligibility": Eligibility.OPEN_ACCESS,
        "accessibility": AccessibilityStatus.STEP_FREE,
        "status": ResourceStatus.OPEN,
        "capacity": (4, 0, 0, CapacityFreshness.STALE),
    },
    {
        "code": "RES-SOUTH-FULL-BEDS",
        "name": "Full Capacity Demo Shelter",
        "category": NeedCategory.TEMPORARY_SHELTER,
        "zone": HarborZone.SOUTH,
        "eligibility": Eligibility.OPEN_ACCESS,
        "accessibility": AccessibilityStatus.LIMITED,
        "status": ResourceStatus.OPEN,
        "capacity": (2, 2, 0, CapacityFreshness.CURRENT),
    },
]

HARBOR_NEEDS: list[HarborNeedSeed] = [
    {
        "request_ref": "DEMO-FOOD-100",
        "category": NeedCategory.FOOD,
        "zone": HarborZone.CENTRAL,
        "quantity": 4,
        "eligibility": Eligibility.OPEN_ACCESS,
        "accessibility_requirement": AccessibilityRequirement.NONE,
        "urgency": NeedUrgency.STANDARD,
        "status": NeedStatus.SUBMITTED,
    },
    {
        "request_ref": "DEMO-SHELTER-200",
        "category": NeedCategory.TEMPORARY_SHELTER,
        "zone": HarborZone.NORTH,
        "quantity": 2,
        "eligibility": Eligibility.COORDINATOR_REFERRAL,
        "accessibility_requirement": AccessibilityRequirement.STEP_FREE,
        "urgency": NeedUrgency.TIME_SENSITIVE,
        "status": NeedStatus.TRIAGED,
        "triage_decision": TriageDecision.READY,
        "triage_reason": TriageReason.MATCH_EXPLANATION_REVIEWED,
    },
    {
        "request_ref": "DEMO-TRANSIT-300",
        "category": NeedCategory.TRANSPORTATION,
        "zone": HarborZone.SOUTH,
        "quantity": 1,
        "eligibility": Eligibility.OPEN_ACCESS,
        "accessibility_requirement": AccessibilityRequirement.NONE,
        "urgency": NeedUrgency.STANDARD,
        "status": NeedStatus.SUBMITTED,
    },
]


def seed_demo_data(db: Session) -> None:
    """Idempotently create the deterministic demo organizations and users."""

    organizations: dict[str, Organization] = {}
    for demo_org in DEMO_ORGANIZATIONS:
        org_id = _stable_id("organization", demo_org.slug)
        organization = db.get(Organization, org_id)
        if organization is None:
            organization = Organization(id=org_id, slug=demo_org.slug, name=demo_org.name)
            db.add(organization)
        else:
            organization.name = demo_org.name
        organizations[demo_org.slug] = organization

    db.flush()

    for demo_user in DEMO_USERS:
        user_id = _stable_id("user", demo_user.email)
        user = db.get(User, user_id)
        if user is None:
            user = User(
                id=user_id,
                email=demo_user.email,
                full_name=demo_user.full_name,
                password_hash=hash_password(DEMO_PASSWORD),
            )
            db.add(user)
        else:
            user.full_name = demo_user.full_name

        db.flush()

        organization = organizations[demo_user.org_slug]
        membership_id = _stable_id("membership", demo_user.email, demo_user.org_slug)
        membership = db.get(Membership, membership_id)
        if membership is None:
            db.add(
                Membership(
                    id=membership_id,
                    user_id=user.id,
                    organization_id=organization.id,
                    role=demo_user.role,
                )
            )
        else:
            membership.role = demo_user.role

    db.flush()
    harbor_org = organizations["zion-demo"]
    for resource_item in HARBOR_RESOURCES:
        resource_id = _stable_id("harbor-resource", str(resource_item["code"]))
        resource = db.get(HarborResource, resource_id)
        values: dict[str, object] = {
            key: value for key, value in resource_item.items() if key != "capacity"
        }
        if resource is None:
            resource = HarborResource(
                id=resource_id, organization_id=harbor_org.id, **values
            )
            db.add(resource)
        else:
            for key, resource_value in values.items():
                setattr(resource, key, resource_value)
        total, reserved, fulfilled, freshness = resource_item["capacity"]
        capacity = db.get(HarborCapacity, resource_id)
        if capacity is None:
            capacity = HarborCapacity(
                resource_id=resource_id,
                organization_id=harbor_org.id,
                total_units=total,
                reserved_units=reserved,
                fulfilled_units=fulfilled,
                freshness=freshness,
                observed_at=_HARBOR_OBSERVED_AT,
            )
            db.add(capacity)
        else:
            capacity.total_units = total
            capacity.reserved_units = reserved
            capacity.fulfilled_units = fulfilled
            capacity.freshness = freshness
            capacity.observed_at = _HARBOR_OBSERVED_AT

    for need_item in HARBOR_NEEDS:
        need_id = _stable_id("harbor-need", str(need_item["request_ref"]))
        need = db.get(HarborNeed, need_id)
        if need is None:
            db.add(HarborNeed(id=need_id, organization_id=harbor_org.id, **need_item))
        else:
            for key, need_value in need_item.items():
                setattr(need, key, need_value)

    volunteer = next(user for user in DEMO_USERS if user.role == Role.VOLUNTEER)
    volunteer_user_id = _stable_id("user", volunteer.email)
    for code, zone, category in [
        ("VOL-CENTRAL-FOOD", HarborZone.CENTRAL, NeedCategory.FOOD),
        ("VOL-NORTH-SHELTER", HarborZone.NORTH, NeedCategory.TEMPORARY_SHELTER),
    ]:
        availability_id = _stable_id("harbor-volunteer", code)
        if db.get(HarborVolunteerAvailability, availability_id) is None:
            db.add(
                HarborVolunteerAvailability(
                    id=availability_id,
                    organization_id=harbor_org.id,
                    user_id=volunteer_user_id,
                    code=code,
                    zone=zone,
                    category=category,
                    available=True,
                )
            )
    ensure_workflow_definition(db)


def main() -> None:
    """Entry point for ``python -m zion_api.seed``."""

    from zion_api.core.config import get_settings

    settings = get_settings()
    engine = get_engine(settings.database_url)
    with Session(engine) as db:
        seed_demo_data(db)
        db.commit()
    print("Seeded deterministic Zion demo data.")  # noqa: T201


if __name__ == "__main__":
    main()
