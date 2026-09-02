"""Beacon reliability: idempotency, retries, timeouts, dead letter, replay."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from tests.beacon_helpers import RUNS_URL, login, start_run
from zion_api.services.beacon.tools import OutOfPolicyToolError, resolve_tool


def test_duplicate_trigger_returns_the_same_run(seeded_client: TestClient) -> None:
    headers = login(seeded_client, "coordinator@zion.example")

    first = start_run(seeded_client, headers, "same-key")
    second = start_run(seeded_client, headers, "same-key")

    assert first["created"] is True
    assert second["created"] is False
    assert second["run"]["id"] == first["run"]["id"]
    # No duplicate side effects: still exactly one run listed.
    listing = seeded_client.get(RUNS_URL, headers=headers).json()
    assert len(listing["runs"]) == 1


def test_reusing_an_idempotency_key_with_a_different_scenario_conflicts(
    seeded_client: TestClient,
) -> None:
    headers = login(seeded_client, "coordinator@zion.example")
    start_run(seeded_client, headers, "conflict-key", scenario="default")

    response = seeded_client.post(
        RUNS_URL,
        json={"idempotency_key": "conflict-key", "scenario": "injection"},
        headers=headers,
    )

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "run_conflict"


def test_transient_timeout_retries_within_bounds_then_dead_letters(
    seeded_client: TestClient,
) -> None:
    headers = login(seeded_client, "coordinator@zion.example")

    run = start_run(seeded_client, headers, "dl-run", scenario="transient-timeout")["run"]

    assert run["status"] == "dead_letter"
    attempts = [step for step in run["steps"] if step["step_key"] == "ingest_hazard_fixture"]
    assert [step["attempt"] for step in attempts] == [1, 2, 3]
    assert all(step["status"] == "timed_out" for step in attempts)
    assert all(step["detail"]["timeout_budget_seconds"] == 2 for step in attempts)
    assert any("dead-letter" in disclosure for disclosure in run["disclosures"])
    assert run["proposal"] is None


def test_replay_recovers_a_dead_letter_run_to_awaiting_approval(
    seeded_client: TestClient,
) -> None:
    headers = login(seeded_client, "coordinator@zion.example")
    run_id = start_run(seeded_client, headers, "replay-run", scenario="transient-timeout")[
        "run"
    ]["id"]

    response = seeded_client.post(f"{RUNS_URL}/{run_id}/replay", headers=headers)

    assert response.status_code == 200
    run = response.json()
    assert run["status"] == "awaiting_approval"
    assert run["replay_count"] == 1
    assert run["metrics"]["retries"] >= 2  # the timed-out attempts stay on record
    assert run["proposal"]["status"] == "proposed"


def test_replay_is_rejected_for_runs_that_are_not_dead_lettered(
    seeded_client: TestClient,
) -> None:
    headers = login(seeded_client, "coordinator@zion.example")
    run_id = start_run(seeded_client, headers, "no-replay")["run"]["id"]

    response = seeded_client.post(f"{RUNS_URL}/{run_id}/replay", headers=headers)

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "run_conflict"


def test_tools_outside_the_typed_allowlist_are_rejected() -> None:
    for name in ("shell_exec", "purchase_supplies", "http_fetch", "", "fixture_loader; rm"):
        with pytest.raises(OutOfPolicyToolError):
            resolve_tool(name)


def test_the_replayed_run_is_the_same_run_not_a_duplicate(seeded_client: TestClient) -> None:
    headers = login(seeded_client, "coordinator@zion.example")
    run_id = start_run(seeded_client, headers, "replay-same", scenario="transient-timeout")[
        "run"
    ]["id"]
    seeded_client.post(f"{RUNS_URL}/{run_id}/replay", headers=headers)

    listing = seeded_client.get(RUNS_URL, headers=headers).json()

    assert [run["id"] for run in listing["runs"]] == [run_id]
