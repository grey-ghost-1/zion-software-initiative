"""Beacon workflow lifecycle: capabilities, state machine, approval, metrics."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from tests.beacon_helpers import RUNS_URL, login, start_run
from zion_api.models.enums import RunStatus
from zion_api.services.beacon import engine
from zion_api.services.beacon.tools import TOOL_REGISTRY

EXPECTED_STEPS = [
    "ingest_hazard_fixture",
    "validate_geospatial_layer",
    "record_provenance",
    "evaluate_policy",
    "plan_allocation",
    "await_human_approval",
]


def test_capabilities_lists_the_fixed_workflow_and_typed_allowlisted_tools(
    client: TestClient,
) -> None:
    response = client.get("/beacon/capabilities")

    assert response.status_code == 200
    body = response.json()
    assert body["workflow_key"] == "coastal-storm-readiness"
    assert body["policy_version"] == "beacon-policy-v1"
    assert [step["step_key"] for step in body["steps"]] == [*EXPECTED_STEPS, "record_outcome"]
    tool_names = {tool["name"] for tool in body["tools"]}
    assert tool_names == set(TOOL_REGISTRY)
    # No arbitrary or dangerous capability exists in the registry.
    for forbidden in ("shell", "http", "purchase", "dispatch", "warn", "evacuat"):
        assert not any(forbidden in name for name in tool_names)
    for tool in body["tools"]:
        assert tool["timeout_seconds"] > 0
        assert tool["max_attempts"] >= 1
    assert "default" in body["scenarios"]
    assert any("human approval" in guardrail for guardrail in body["guardrails"])


def test_happy_path_runs_every_step_and_pauses_for_human_approval(
    seeded_client: TestClient,
) -> None:
    headers = login(seeded_client, "coordinator@zion.example")

    body = start_run(seeded_client, headers, "run-happy")

    assert body["created"] is True
    run = body["run"]
    assert run["status"] == "awaiting_approval"
    assert [step["step_key"] for step in run["steps"]] == EXPECTED_STEPS
    assert all(step["status"] == "succeeded" for step in run["steps"])
    assert run["policy_version"] == "beacon-policy-v1"
    assert run["fixture_id"] == "beacon-coastal-storm-v1"
    assert run["proposal"]["status"] == "proposed"
    assert run["metrics"]["policy_checks_failed"] == 0
    assert run["metrics"]["step_events"] == len(EXPECTED_STEPS)

    provenance = run["provenance"][0]
    assert provenance["synthetic"] is True
    assert len(provenance["checksum_sha256"]) == 64
    assert provenance["effective_at"] and provenance["retrieved_at"]


def test_approval_completes_the_run_and_records_the_outcome_step(
    seeded_client: TestClient,
) -> None:
    headers = login(seeded_client, "coordinator@zion.example")
    run_id = start_run(seeded_client, headers, "run-approve")["run"]["id"]

    response = seeded_client.post(
        f"{RUNS_URL}/{run_id}/approval",
        json={"decision": "approve", "note": "Demo approval."},
        headers=headers,
    )

    assert response.status_code == 200
    run = response.json()
    assert run["status"] == "completed"
    assert run["proposal"]["status"] == "approved"
    assert run["proposal"]["decided_at"] is not None
    assert run["steps"][-1]["step_key"] == "record_outcome"
    assert run["steps"][-1]["detail"]["autonomous_execution"] is False


def test_rejection_terminates_the_run_without_allocation(seeded_client: TestClient) -> None:
    headers = login(seeded_client, "coordinator@zion.example")
    run_id = start_run(seeded_client, headers, "run-reject")["run"]["id"]

    response = seeded_client.post(
        f"{RUNS_URL}/{run_id}/approval",
        json={"decision": "reject", "note": "Not appropriate."},
        headers=headers,
    )

    assert response.status_code == 200
    run = response.json()
    assert run["status"] == "rejected"
    assert run["proposal"]["status"] == "rejected"


def test_a_decided_run_cannot_be_decided_again(seeded_client: TestClient) -> None:
    headers = login(seeded_client, "coordinator@zion.example")
    run_id = start_run(seeded_client, headers, "run-double")["run"]["id"]
    first = seeded_client.post(
        f"{RUNS_URL}/{run_id}/approval", json={"decision": "approve"}, headers=headers
    )
    assert first.status_code == 200

    second = seeded_client.post(
        f"{RUNS_URL}/{run_id}/approval", json={"decision": "reject"}, headers=headers
    )

    assert second.status_code == 409
    assert second.json()["error"]["code"] == "run_conflict"


def test_run_listing_is_scoped_to_the_organization(seeded_client: TestClient) -> None:
    headers = login(seeded_client, "coordinator@zion.example")
    start_run(seeded_client, headers, "run-list")

    response = seeded_client.get(RUNS_URL, headers=headers)

    assert response.status_code == 200
    body = response.json()
    assert body["organization_slug"] == "zion-demo"
    assert len(body["runs"]) == 1
    assert body["runs"][0]["idempotency_key"] == "run-list"


def test_state_machine_rejects_transitions_outside_the_fixed_graph(
    seeded_db_session: Session,
) -> None:
    from zion_api.models.beacon import WorkflowRun

    run = WorkflowRun(
        workflow_key="coastal-storm-readiness",
        workflow_version="1",
        policy_version="beacon-policy-v1",
        organization_id="org",
        created_by_user_id="user",
        idempotency_key="x",
        scenario="default",
        fixture_id="f",
        status=RunStatus.COMPLETED,
    )

    with pytest.raises(engine.InvalidTransitionError):
        engine.transition(run, RunStatus.RUNNING)
    with pytest.raises(engine.InvalidTransitionError):
        engine.transition(run, RunStatus.DEAD_LETTER)


def test_scenarios_outside_the_allowlist_are_rejected(seeded_client: TestClient) -> None:
    headers = login(seeded_client, "coordinator@zion.example")

    response = seeded_client.post(
        RUNS_URL,
        json={"idempotency_key": "bad", "scenario": "curl http://evil.example"},
        headers=headers,
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"
