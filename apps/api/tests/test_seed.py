"""Seed script determinism and idempotency tests."""

from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from zion_api.models.membership import Membership
from zion_api.models.organization import Organization
from zion_api.models.user import User
from zion_api.seed import DEMO_ORGANIZATIONS, DEMO_USERS, seed_demo_data


def test_seed_creates_exactly_the_declared_demo_data(db_session: Session) -> None:
    seed_demo_data(db_session)
    db_session.commit()

    assert db_session.scalar(select(func.count()).select_from(Organization)) == len(
        DEMO_ORGANIZATIONS
    )
    assert db_session.scalar(select(func.count()).select_from(User)) == len(DEMO_USERS)
    assert db_session.scalar(select(func.count()).select_from(Membership)) == len(DEMO_USERS)


def test_seed_is_idempotent_and_produces_stable_ids(db_session: Session) -> None:
    seed_demo_data(db_session)
    db_session.commit()
    first_user_ids = sorted(u.id for u in db_session.scalars(select(User)).all())

    # Running the seed again must not create duplicates or change identities.
    seed_demo_data(db_session)
    db_session.commit()
    second_user_ids = sorted(u.id for u in db_session.scalars(select(User)).all())

    assert first_user_ids == second_user_ids
    assert db_session.scalar(select(func.count()).select_from(User)) == len(DEMO_USERS)


def test_seed_uses_only_synthetic_example_emails(db_session: Session) -> None:
    seed_demo_data(db_session)
    db_session.commit()

    for user in db_session.scalars(select(User)).all():
        assert user.email.endswith(".example")
