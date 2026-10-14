"""Typed error envelope, validation, and CORS contract tests."""

from __future__ import annotations

from fastapi.testclient import TestClient

from zion_api.core.config import get_settings


def test_unknown_route_returns_the_standard_404_shape(client: TestClient) -> None:
    response = client.get("/does/not/exist")

    assert response.status_code == 404


def test_invalid_request_body_returns_a_typed_validation_error(client: TestClient) -> None:
    response = client.post("/auth/login", json={"email": "admin@zion.example"})

    assert response.status_code == 422
    body = response.json()
    assert body["error"]["code"] == "validation_error"
    assert "request_id" in body["error"]


def test_error_responses_never_include_a_stack_trace(client: TestClient) -> None:
    response = client.post("/auth/login", json={"not": "a login payload"})

    assert response.status_code == 422
    text = response.text.lower()
    assert "traceback" not in text
    assert "file \"" not in text


def test_cors_allows_the_configured_dev_origin(client: TestClient) -> None:
    allowed_origin = get_settings().cors_allowed_origins[0]

    response = client.options(
        "/health/live",
        headers={
            "Origin": allowed_origin,
            "Access-Control-Request-Method": "GET",
        },
    )

    assert response.headers.get("access-control-allow-origin") == allowed_origin


def test_cors_rejects_an_unlisted_origin(client: TestClient) -> None:
    response = client.options(
        "/health/live",
        headers={
            "Origin": "https://not-allowed.example",
            "Access-Control-Request-Method": "GET",
        },
    )

    assert "access-control-allow-origin" not in response.headers
