"""Shared helpers for the Beacon API tests."""

from __future__ import annotations

from typing import Any

from fastapi.testclient import TestClient

from zion_api.seed import DEMO_PASSWORD

ORG = "zion-demo"
RUNS_URL = f"/beacon/organizations/{ORG}/runs"


def login(client: TestClient, email: str) -> dict[str, str]:
    response = client.post("/auth/login", json={"email": email, "password": DEMO_PASSWORD})
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def start_run(
    client: TestClient,
    headers: dict[str, str],
    idempotency_key: str,
    scenario: str = "default",
    org: str = ORG,
) -> dict[str, Any]:
    response = client.post(
        f"/beacon/organizations/{org}/runs",
        json={"idempotency_key": idempotency_key, "scenario": scenario},
        headers=headers,
    )
    assert response.status_code == 200, response.text
    body: dict[str, Any] = response.json()
    return body
