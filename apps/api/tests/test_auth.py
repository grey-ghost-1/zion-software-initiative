"""Login, session-token expiry, and authentication-failure tests."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from zion_api.models.auth_token import AuthToken
from zion_api.seed import DEMO_PASSWORD


def test_login_with_correct_credentials_issues_an_expiring_token(
    seeded_client: TestClient,
) -> None:
    response = seeded_client.post(
        "/auth/login", json={"email": "admin@zion.example", "password": DEMO_PASSWORD}
    )

    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert len(body["access_token"]) > 20
    expires_at = datetime.fromisoformat(body["expires_at"])
    assert expires_at > datetime.now(UTC)


def test_login_with_wrong_password_is_rejected(seeded_client: TestClient) -> None:
    response = seeded_client.post(
        "/auth/login", json={"email": "admin@zion.example", "password": "not-the-password"}
    )

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "invalid_credentials"


def test_login_with_unknown_email_gives_the_same_generic_error(
    seeded_client: TestClient,
) -> None:
    response = seeded_client.post(
        "/auth/login", json={"email": "nobody@zion.example", "password": DEMO_PASSWORD}
    )

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "invalid_credentials"


def test_me_requires_a_bearer_token(seeded_client: TestClient) -> None:
    response = seeded_client.get("/me")

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "invalid_or_expired_token"


def test_me_rejects_a_garbage_token(seeded_client: TestClient) -> None:
    response = seeded_client.get("/me", headers={"Authorization": "Bearer not-a-real-token"})

    assert response.status_code == 401


def test_me_returns_profile_and_roles_for_a_valid_token(seeded_client: TestClient) -> None:
    login = seeded_client.post(
        "/auth/login", json={"email": "admin@zion.example", "password": DEMO_PASSWORD}
    )
    token = login.json()["access_token"]

    response = seeded_client.get("/me", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    body = response.json()
    assert body["email"] == "admin@zion.example"
    expected_membership = {
        "organization_slug": "zion-demo",
        "organization_name": "Zion Demo Cooperative",
        "role": "admin",
    }
    assert expected_membership in body["memberships"]


def test_expired_token_is_rejected(
    seeded_client: TestClient, seeded_db_session: Session
) -> None:
    login = seeded_client.post(
        "/auth/login", json={"email": "admin@zion.example", "password": DEMO_PASSWORD}
    )
    token = login.json()["access_token"]

    # Force the freshly issued token to have already expired.
    stored_token = seeded_db_session.scalar(select(AuthToken))
    assert stored_token is not None
    stored_token.expires_at = datetime.now(UTC) - timedelta(minutes=1)
    seeded_db_session.commit()

    response = seeded_client.get("/me", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "invalid_or_expired_token"


def test_revoked_token_is_rejected(
    seeded_client: TestClient, seeded_db_session: Session
) -> None:
    login = seeded_client.post(
        "/auth/login", json={"email": "admin@zion.example", "password": DEMO_PASSWORD}
    )
    token = login.json()["access_token"]

    stored_token = seeded_db_session.scalar(select(AuthToken))
    assert stored_token is not None
    stored_token.revoked_at = datetime.now(UTC)
    seeded_db_session.commit()

    response = seeded_client.get("/me", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 401
