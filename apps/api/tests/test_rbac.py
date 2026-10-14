"""Role-based access control and cross-organization isolation tests."""

from __future__ import annotations

from fastapi.testclient import TestClient

from zion_api.seed import DEMO_PASSWORD


def _login(client: TestClient, email: str) -> str:
    response = client.post("/auth/login", json={"email": email, "password": DEMO_PASSWORD})
    assert response.status_code == 200
    token: str = response.json()["access_token"]
    return token


def test_admin_can_list_members_of_their_own_organization(seeded_client: TestClient) -> None:
    token = _login(seeded_client, "admin@zion.example")

    response = seeded_client.get(
        "/admin/organizations/zion-demo/members", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    emails = {member["email"] for member in response.json()["members"]}
    assert emails == {
        "admin@zion.example",
        "coordinator@zion.example",
        "navigator@zion.example",
        "volunteer@zion.example",
        "visitor@zion.example",
    }


def test_non_admin_role_is_denied_the_admin_endpoint(seeded_client: TestClient) -> None:
    token = _login(seeded_client, "volunteer@zion.example")

    response = seeded_client.get(
        "/admin/organizations/zion-demo/members", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 403
    assert response.json()["error"]["code"] == "role_denied"


def test_admin_of_one_organization_cannot_access_a_different_organization(
    seeded_client: TestClient,
) -> None:
    token = _login(seeded_client, "admin@zion.example")

    response = seeded_client.get(
        "/admin/organizations/zion-demo-alliance/members",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "organization_not_found"


def test_admin_of_the_other_organization_can_access_their_own(
    seeded_client: TestClient,
) -> None:
    token = _login(seeded_client, "admin@alliance.zion.example")

    response = seeded_client.get(
        "/admin/organizations/zion-demo-alliance/members",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json()["organization_slug"] == "zion-demo-alliance"


def test_nonexistent_organization_gives_the_same_404_as_denied_access(
    seeded_client: TestClient,
) -> None:
    token = _login(seeded_client, "admin@zion.example")

    response = seeded_client.get(
        "/admin/organizations/does-not-exist/members",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "organization_not_found"
