"""Audit event tests: written on login/admin action, and append-only."""

from __future__ import annotations

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from zion_api.db.audit_guard import AuditEventImmutableError
from zion_api.models.audit_event import AuditEvent
from zion_api.seed import DEMO_PASSWORD


def test_login_writes_an_audit_event(
    seeded_client: TestClient, seeded_db_session: Session
) -> None:
    seeded_client.post(
        "/auth/login", json={"email": "admin@zion.example", "password": DEMO_PASSWORD}
    )

    events = seeded_db_session.scalars(
        select(AuditEvent).where(AuditEvent.action == "auth.login")
    ).all()
    assert len(events) == 1
    assert events[0].subject_type == "user"


def test_failed_login_does_not_write_an_audit_event(
    seeded_client: TestClient, seeded_db_session: Session
) -> None:
    seeded_client.post(
        "/auth/login", json={"email": "admin@zion.example", "password": "wrong"}
    )

    events = seeded_db_session.scalars(select(AuditEvent)).all()
    assert events == []


def test_admin_action_writes_an_audit_event_scoped_to_the_organization(
    seeded_client: TestClient, seeded_db_session: Session
) -> None:
    login = seeded_client.post(
        "/auth/login", json={"email": "admin@zion.example", "password": DEMO_PASSWORD}
    )
    token = login.json()["access_token"]

    seeded_client.get(
        "/admin/organizations/zion-demo/members", headers={"Authorization": f"Bearer {token}"}
    )

    event = seeded_db_session.scalar(
        select(AuditEvent).where(AuditEvent.action == "admin.members_viewed")
    )
    assert event is not None
    assert event.subject_type == "organization"
    assert event.context["member_count"] == 5


def test_audit_events_cannot_be_updated(db_session: Session) -> None:
    event = AuditEvent(action="auth.login", actor_user_id="u1", context={})
    db_session.add(event)
    db_session.commit()

    event.action = "tampered"
    try:
        db_session.commit()
        raised = False
    except AuditEventImmutableError:
        raised = True
        db_session.rollback()

    assert raised


def test_audit_events_cannot_be_deleted(db_session: Session) -> None:
    event = AuditEvent(action="auth.login", actor_user_id="u1", context={})
    db_session.add(event)
    db_session.commit()

    db_session.delete(event)
    try:
        db_session.commit()
        raised = False
    except AuditEventImmutableError:
        raised = True
        db_session.rollback()

    assert raised
