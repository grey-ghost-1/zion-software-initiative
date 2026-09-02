"""Haven plan lifecycle tests: org-scoped create/review/close, audit events,
cross-organization and role denial, and no sensitive persistence or logging."""

from __future__ import annotations

import logging
from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import inspect, select
from sqlalchemy.orm import Session

from zion_api.haven_seed import seed_haven_content
from zion_api.main import app
from zion_api.models.audit_event import AuditEvent
from zion_api.models.haven import HavenNavigationPlan
from zion_api.routes.haven import get_optional_db
from zion_api.seed import DEMO_PASSWORD

SENSITIVE_TEXT = "synthetic-marker-text-that-must-never-persist-anywhere-9137"

PLAN_PAYLOAD = {
    "concern_category": "stress_or_anxiety",
    "duration": "over_one_week",
    "severity": "moderate",
    "self_harm_risk": False,
    "concern_text": SENSITIVE_TEXT,
}


@pytest.fixture
def haven_client(seeded_db_session: Session, seeded_client: TestClient) -> Iterator[TestClient]:
    seed_haven_content(seeded_db_session)
    seeded_db_session.commit()

    def override() -> Iterator[Session | None]:
        yield seeded_db_session

    app.dependency_overrides[get_optional_db] = override
    try:
        yield seeded_client
    finally:
        app.dependency_overrides.pop(get_optional_db, None)


def _login(client: TestClient, email: str) -> dict[str, str]:
    response = client.post("/auth/login", json={"email": email, "password": DEMO_PASSWORD})
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def _create_plan(client: TestClient, headers: dict[str, str]) -> dict:
    response = client.post(
        "/haven/organizations/zion-demo/plans", json=PLAN_PAYLOAD, headers=headers
    )
    assert response.status_code == 201
    return response.json()


def test_navigator_can_create_review_and_close_a_plan(
    haven_client: TestClient, seeded_db_session: Session
) -> None:
    headers = _login(haven_client, "navigator@zion.example")
    created = _create_plan(haven_client, headers)

    plan = created["plan"]
    assert plan["organization_slug"] == "zion-demo"
    assert plan["synthetic"] is True
    assert plan["status"] == "open"
    assert plan["routed_outcome"] == "mental_health_support"
    assert created["navigation"]["stored"] is True

    listed = haven_client.get("/haven/organizations/zion-demo/plans", headers=headers)
    assert listed.status_code == 200
    assert {p["id"] for p in listed.json()["plans"]} == {plan["id"]}

    reviewed = haven_client.post(
        f"/haven/organizations/zion-demo/plans/{plan['id']}/review",
        json={"reason_code": "routing_confirmed"},
        headers=headers,
    )
    assert reviewed.status_code == 200
    assert reviewed.json()["plan"]["status"] == "reviewed"
    assert reviewed.json()["plan"]["review_reason_code"] == "routing_confirmed"

    closed = haven_client.post(
        f"/haven/organizations/zion-demo/plans/{plan['id']}/close", headers=headers
    )
    assert closed.status_code == 200
    assert closed.json()["plan"]["status"] == "closed"
    assert closed.json()["plan"]["closed_at"] is not None

    actions = seeded_db_session.scalars(
        select(AuditEvent.action).where(AuditEvent.subject_id == plan["id"])
    ).all()
    assert sorted(actions) == [
        "haven.plan_closed",
        "haven.plan_created",
        "haven.plan_reviewed",
    ]


def test_free_text_review_annotation_is_rejected(haven_client: TestClient) -> None:
    headers = _login(haven_client, "navigator@zion.example")
    plan = _create_plan(haven_client, headers)["plan"]

    response = haven_client.post(
        f"/haven/organizations/zion-demo/plans/{plan['id']}/review",
        json={"reason_code": "my own free-form note"},
        headers=headers,
    )
    assert response.status_code == 422


def test_visitor_and_volunteer_roles_are_denied_plan_endpoints(
    haven_client: TestClient,
) -> None:
    for email in ("visitor@zion.example", "volunteer@zion.example"):
        headers = _login(haven_client, email)
        response = haven_client.post(
            "/haven/organizations/zion-demo/plans", json=PLAN_PAYLOAD, headers=headers
        )
        assert response.status_code == 403
        assert response.json()["error"]["code"] == "role_denied"

        response = haven_client.get("/haven/organizations/zion-demo/plans", headers=headers)
        assert response.status_code == 403


def test_unauthenticated_callers_cannot_touch_plan_endpoints(haven_client: TestClient) -> None:
    assert haven_client.get("/haven/organizations/zion-demo/plans").status_code == 401
    assert (
        haven_client.post("/haven/organizations/zion-demo/plans", json=PLAN_PAYLOAD).status_code
        == 401
    )


def test_cross_organization_access_is_denied_without_leaking_existence(
    haven_client: TestClient,
) -> None:
    navigator_headers = _login(haven_client, "navigator@zion.example")
    plan = _create_plan(haven_client, navigator_headers)["plan"]

    alliance_headers = _login(haven_client, "admin@alliance.zion.example")

    # Alliance admin is not a member of zion-demo: identical org 404.
    response = haven_client.get(
        "/haven/organizations/zion-demo/plans", headers=alliance_headers
    )
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "organization_not_found"

    # Reaching another org's plan through their own org yields a plan 404,
    # never a hint that the plan exists.
    response = haven_client.post(
        f"/haven/organizations/zion-demo-alliance/plans/{plan['id']}/review",
        json={"reason_code": "routing_confirmed"},
        headers=alliance_headers,
    )
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "plan_not_found"

    response = haven_client.post(
        f"/haven/organizations/zion-demo-alliance/plans/{plan['id']}/close",
        headers=alliance_headers,
    )
    assert response.status_code == 404


def test_plans_persist_only_controlled_values_never_free_text(
    haven_client: TestClient, seeded_db_session: Session
) -> None:
    headers = _login(haven_client, "navigator@zion.example")
    plan_id = _create_plan(haven_client, headers)["plan"]["id"]

    stored = seeded_db_session.get(HavenNavigationPlan, plan_id)
    assert stored is not None

    columns = {column.key for column in inspect(HavenNavigationPlan).columns}
    for forbidden in ("concern_text", "notes", "narrative", "location", "dob", "name"):
        assert forbidden not in columns

    for column in inspect(HavenNavigationPlan).columns:
        value = getattr(stored, column.key)
        assert SENSITIVE_TEXT not in str(value)

    events = seeded_db_session.scalars(select(AuditEvent)).all()
    for event in events:
        assert SENSITIVE_TEXT not in str(event.context)
        assert event.subject_type != "concern_text"


def test_concern_text_is_never_logged(
    haven_client: TestClient, caplog: pytest.LogCaptureFixture
) -> None:
    headers = _login(haven_client, "navigator@zion.example")
    with caplog.at_level(logging.DEBUG):
        _create_plan(haven_client, headers)
        haven_client.post(
            "/haven/navigations",
            json={
                "concern_category": "general_question",
                "duration": "under_one_day",
                "severity": "mild",
                "concern_text": SENSITIVE_TEXT,
            },
        )
    assert SENSITIVE_TEXT not in caplog.text


def test_ephemeral_public_navigation_persists_nothing(
    haven_client: TestClient, seeded_db_session: Session
) -> None:
    before_plans = seeded_db_session.scalars(select(HavenNavigationPlan.id)).all()
    before_audit = seeded_db_session.scalars(select(AuditEvent.id)).all()

    response = haven_client.post(
        "/haven/navigations",
        json={
            "concern_category": "low_mood",
            "duration": "over_one_week",
            "severity": "moderate",
            "concern_text": SENSITIVE_TEXT,
        },
    )
    assert response.status_code == 200
    assert response.json()["stored"] is False

    assert seeded_db_session.scalars(select(HavenNavigationPlan.id)).all() == before_plans
    assert seeded_db_session.scalars(select(AuditEvent.id)).all() == before_audit
