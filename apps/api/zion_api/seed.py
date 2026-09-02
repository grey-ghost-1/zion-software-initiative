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

from sqlalchemy.orm import Session

from zion_api.core.security import hash_password
from zion_api.db.session import get_engine
from zion_api.models.enums import Role
from zion_api.models.membership import Membership
from zion_api.models.organization import Organization
from zion_api.models.user import User

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
