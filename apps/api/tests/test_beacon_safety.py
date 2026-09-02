"""Beacon safety: injection containment, sanitized logging, RBAC, geo rejects."""

from __future__ import annotations

from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from tests.beacon_helpers import RUNS_URL, login, start_run
from zion_api.models.audit_event import AuditEvent
from zion_api.models.beacon import WorkflowRunStep
from zion_api.services.beacon import engine
from zion_api.services.beacon.fixtures import Scenario, load_fixture
from zion_api.services.beacon.policy import evaluate_policy

INJECTED_MARKERS = ("IGNORE ALL PREVIOUS INSTRUCTIONS", "shell_exec", "purchase_supplies")


def test_injection_text_cannot_alter_steps_tools_or_policy(seeded_client: TestClient) -> None:
    headers = login(seeded_client, "coordinator@zion.example")

    baseline = start_run(seeded_client, headers, "base")["run"]
    injected = start_run(seeded_client, headers, "inj", scenario="injection")["run"]

    assert [step["step_key"] for step in injected["steps"]] == [
        step["step_key"] for step in baseline["steps"]
    ]
    assert [step["tool_name"] for step in injected["steps"]] == [
        step["tool_name"] for step in baseline["steps"]
    ]
    assert injected["policy_version"] == baseline["policy_version"]
    assert injected["status"] == "awaiting_approval"  # still requires a human

    guard = next(
        check for check in injected["policy_results"] if check["check"] == "prompt_injection_guard"
    )
    assert guard["passed"] is True
    assert guard["detail"]["suspicious_markers"] >= 3
    assert guard["detail"]["treated_as_data"] is True


def test_injected_and_sensitive_text_is_never_persisted(
    seeded_client: TestClient, seeded_db_session: Session
) -> None:
    headers = login(seeded_client, "coordinator@zion.example")
    start_run(seeded_client, headers, "inj-2", scenario="injection")
    start_run(seeded_client, headers, "sens-2", scenario="sensitive-data")

    steps = seeded_db_session.scalars(select(WorkflowRunStep)).all()
    audits = seeded_db_session.scalars(select(AuditEvent)).all()
    persisted_blobs = [str(step.detail) for step in steps] + [
        str(audit.context) for audit in audits
    ]

    for blob in persisted_blobs:
        for marker in INJECTED_MARKERS:
            assert marker not in blob
        assert "123-45-6789" not in blob
        assert "jane.doe@example.com" not in blob


def test_sensitive_data_scenario_discloses_redaction_without_storing_text(
    seeded_client: TestClient,
) -> None:
    headers = login(seeded_client, "coordinator@zion.example")

    run = start_run(seeded_client, headers, "sens", scenario="sensitive-data")["run"]

    guard = next(
        check for check in run["policy_results"] if check["check"] == "sensitive_data_guard"
    )
    assert guard["detail"]["redacted_markers"] >= 2
    assert guard["detail"]["raw_text_stored"] is False
    assert any("redacted" in disclosure for disclosure in run["disclosures"])


@pytest.mark.parametrize(
    ("scenario", "expected_code"),
    [
        ("invalid-crs", "unsupported_crs"),
        ("malformed-geometry", "null_geometry"),
        ("impossible-coordinates", "impossible_coordinates"),
        ("stale-data", "stale_observation"),
    ],
)
def test_bad_geospatial_fixtures_are_rejected_with_disclosed_codes(
    seeded_client: TestClient, scenario: str, expected_code: str
) -> None:
    headers = login(seeded_client, "coordinator@zion.example")

    run = start_run(seeded_client, headers, f"geo-{scenario}", scenario=scenario)["run"]

    assert run["status"] == "failed"
    assert any(expected_code in disclosure for disclosure in run["disclosures"])
    assert run["proposal"] is None


def test_antimeridian_crossing_is_disclosed_but_not_fatal(seeded_client: TestClient) -> None:
    headers = login(seeded_client, "coordinator@zion.example")

    run = start_run(seeded_client, headers, "anti", scenario="antimeridian")["run"]

    assert run["status"] == "awaiting_approval"
    assert any("antimeridian_crossing" in disclosure for disclosure in run["disclosures"])


def test_stale_fixture_fails_the_versioned_freshness_policy_check() -> None:
    fixture = load_fixture(Scenario.STALE_DATA)
    as_of = datetime.fromisoformat(fixture["as_of"])

    checks = {check.check: check for check in evaluate_policy(fixture, as_of)}

    assert checks["fixture_freshness"].passed is False
    assert checks["fixture_is_synthetic"].passed is True


def test_volunteer_cannot_approve_reject_or_replay(seeded_client: TestClient) -> None:
    coordinator = login(seeded_client, "coordinator@zion.example")
    volunteer = login(seeded_client, "volunteer@zion.example")
    run_id = start_run(seeded_client, coordinator, "rbac-run")["run"]["id"]
    dead_id = start_run(seeded_client, coordinator, "rbac-dl", scenario="transient-timeout")[
        "run"
    ]["id"]

    approve = seeded_client.post(
        f"{RUNS_URL}/{run_id}/approval", json={"decision": "approve"}, headers=volunteer
    )
    replay = seeded_client.post(f"{RUNS_URL}/{dead_id}/replay", headers=volunteer)

    assert approve.status_code == 403
    assert approve.json()["error"]["code"] == "role_denied"
    assert replay.status_code == 403


def test_runs_are_isolated_between_organizations(seeded_client: TestClient) -> None:
    coordinator = login(seeded_client, "coordinator@zion.example")
    other_admin = login(seeded_client, "admin@alliance.zion.example")
    run_id = start_run(seeded_client, coordinator, "iso-run")["run"]["id"]

    # The other organization's admin cannot see or decide the run at all.
    view = seeded_client.get(
        f"/beacon/organizations/zion-demo/runs/{run_id}", headers=other_admin
    )
    assert view.status_code == 404

    cross = seeded_client.get(
        f"/beacon/organizations/zion-demo-alliance/runs/{run_id}", headers=other_admin
    )
    assert cross.status_code == 404
    assert cross.json()["error"]["code"] == "run_not_found"


def test_approval_and_replay_actions_are_audited(
    seeded_client: TestClient, seeded_db_session: Session
) -> None:
    headers = login(seeded_client, "coordinator@zion.example")
    run_id = start_run(seeded_client, headers, "audit-run")["run"]["id"]
    seeded_client.post(
        f"{RUNS_URL}/{run_id}/approval", json={"decision": "approve"}, headers=headers
    )

    actions = set(
        seeded_db_session.scalars(
            select(AuditEvent.action).where(AuditEvent.subject_id == run_id)
        ).all()
    )

    assert {"beacon.run_started", "beacon.allocation_approved"} <= actions


def test_tampered_definitions_cannot_execute_unregistered_tools(
    seeded_db_session: Session,
) -> None:
    # Even if a stored definition were tampered with, execution resolves tools
    # only through the typed registry, which rejects unknown names.
    from zion_api.services.beacon.tools import OutOfPolicyToolError, resolve_tool

    definition = engine.ensure_workflow_definition(seeded_db_session)
    tampered: list[dict[str, object]] = [
        *definition.steps,
        {"step_key": "exfiltrate", "tool": "shell_exec"},
    ]

    with pytest.raises(OutOfPolicyToolError):
        for step in tampered:
            resolve_tool(str(step["tool"]))
