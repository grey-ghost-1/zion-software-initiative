"""Deterministic Beacon workflow engine.

One fixed state machine, one fixed step list, one typed tool registry -- all
defined in code, never in user or fixture input. Execution is synchronous and
deterministic: retries, timeouts, and dead-letter transitions are driven by
fixture flags so every behavior is reproducible in tests.
"""

from __future__ import annotations

import uuid
from collections.abc import Callable
from datetime import datetime
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from zion_api.core.security import utcnow
from zion_api.models.beacon import (
    AllocationProposal,
    FixtureProvenance,
    WorkflowDefinition,
    WorkflowRun,
    WorkflowRunStep,
)
from zion_api.models.enums import ProposalStatus, RunStatus, StepStatus
from zion_api.services.beacon import allocation as allocation_service
from zion_api.services.beacon import fixtures, geo
from zion_api.services.beacon import policy as policy_service
from zion_api.services.beacon.tools import (
    StepValidationError,
    ToolTimeoutError,
    resolve_tool,
)

WORKFLOW_KEY = "coastal-storm-readiness"
WORKFLOW_VERSION = "1"
WORKFLOW_NAME = "Coastal storm readiness (synthetic demonstration)"

# The fixed step list. Fixture content can never add, remove, or reorder steps.
WORKFLOW_STEPS: tuple[tuple[str, str], ...] = (
    ("ingest_hazard_fixture", "fixture_loader"),
    ("validate_geospatial_layer", "geo_validator"),
    ("record_provenance", "provenance_recorder"),
    ("evaluate_policy", "policy_evaluator"),
    ("plan_allocation", "allocation_planner"),
    ("await_human_approval", "approval_gate"),
)
OUTCOME_STEP: tuple[str, str] = ("record_outcome", "outcome_recorder")

ALLOWED_TRANSITIONS: dict[RunStatus, frozenset[RunStatus]] = {
    RunStatus.RECEIVED: frozenset({RunStatus.RUNNING}),
    RunStatus.RUNNING: frozenset(
        {RunStatus.AWAITING_APPROVAL, RunStatus.FAILED, RunStatus.DEAD_LETTER}
    ),
    RunStatus.AWAITING_APPROVAL: frozenset({RunStatus.APPROVED, RunStatus.REJECTED}),
    RunStatus.APPROVED: frozenset({RunStatus.COMPLETED}),
    RunStatus.DEAD_LETTER: frozenset({RunStatus.RUNNING}),
    RunStatus.COMPLETED: frozenset(),
    RunStatus.REJECTED: frozenset(),
    RunStatus.FAILED: frozenset(),
}

_DEFINITION_NAMESPACE = uuid.UUID("7c1b1a52-52e5-4a6b-8a3e-2f14b7c0a9d3")


class InvalidTransitionError(RuntimeError):
    """Raised when the engine would leave the fixed state machine."""


class IdempotencyConflict(RuntimeError):
    """Raised when an idempotency key is reused with a different scenario."""


class RunStateConflict(RuntimeError):
    """Raised when an action is invalid for the run's current state."""


def ensure_workflow_definition(db: Session) -> WorkflowDefinition:
    """Get or create the single seeded Beacon workflow definition."""

    definition = db.scalar(
        select(WorkflowDefinition).where(WorkflowDefinition.key == WORKFLOW_KEY)
    )
    if definition is None:
        definition = WorkflowDefinition(
            id=str(uuid.uuid5(_DEFINITION_NAMESPACE, WORKFLOW_KEY)),
            key=WORKFLOW_KEY,
            version=WORKFLOW_VERSION,
            name=WORKFLOW_NAME,
            policy_version=policy_service.POLICY_VERSION,
            steps=[
                {"step_key": step_key, "tool": tool_name}
                for step_key, tool_name in (*WORKFLOW_STEPS, OUTCOME_STEP)
            ],
        )
        db.add(definition)
        db.flush()
    return definition


def transition(run: WorkflowRun, new_status: RunStatus) -> None:
    """Apply one state-machine transition, rejecting anything not allowed."""

    if new_status not in ALLOWED_TRANSITIONS[run.status]:
        raise InvalidTransitionError(
            f"Transition {run.status.value} -> {new_status.value} is not allowed."
        )
    run.status = new_status


def start_run(
    db: Session,
    *,
    organization_id: str,
    user_id: str,
    idempotency_key: str,
    scenario: fixtures.Scenario,
) -> tuple[WorkflowRun, bool]:
    """Start (or idempotently return) one run for an organization."""

    existing = db.scalar(
        select(WorkflowRun).where(
            WorkflowRun.organization_id == organization_id,
            WorkflowRun.idempotency_key == idempotency_key,
        )
    )
    if existing is not None:
        if existing.scenario != scenario.value:
            raise IdempotencyConflict(
                "This idempotency key was already used with a different scenario."
            )
        return existing, False

    definition = ensure_workflow_definition(db)
    run = WorkflowRun(
        workflow_key=definition.key,
        workflow_version=definition.version,
        policy_version=definition.policy_version,
        organization_id=organization_id,
        created_by_user_id=user_id,
        idempotency_key=idempotency_key,
        scenario=scenario.value,
        fixture_id=fixtures.FIXTURE_ID,
        status=RunStatus.RECEIVED,
        policy_results=[],
        metrics={},
        disclosures=[],
        replay_count=0,
    )
    db.add(run)
    db.flush()
    _execute(db, run, replay=False)
    return run, True


def replay_run(db: Session, run: WorkflowRun) -> WorkflowRun:
    """Safely replay a dead-lettered run after simulated upstream recovery."""

    if run.status is not RunStatus.DEAD_LETTER:
        raise RunStateConflict("Only dead-letter runs can be replayed.")
    run.replay_count += 1
    _execute(db, run, replay=True)
    return run


def decide_allocation(
    db: Session,
    run: WorkflowRun,
    *,
    decided_by_user_id: str,
    approve: bool,
    note: str | None,
) -> AllocationProposal:
    """Record the human approve/reject decision and finish the run."""

    if run.status is not RunStatus.AWAITING_APPROVAL:
        raise RunStateConflict("This run is not awaiting approval.")
    proposal = db.scalar(
        select(AllocationProposal).where(AllocationProposal.run_id == run.id)
    )
    if proposal is None or proposal.status is not ProposalStatus.PROPOSED:
        raise RunStateConflict("This run has no pending allocation proposal.")

    proposal.status = ProposalStatus.APPROVED if approve else ProposalStatus.REJECTED
    proposal.decided_by_user_id = decided_by_user_id
    proposal.decided_at = utcnow()
    proposal.decision_note = note

    step_key, tool_name = OUTCOME_STEP
    spec = resolve_tool(tool_name)
    _record_step(
        db,
        run,
        step_key=step_key,
        tool_name=spec.name,
        attempt=1,
        status=StepStatus.SUCCEEDED,
        detail={
            "decision": "approved" if approve else "rejected",
            "decided_by_role_gate": ["coordinator", "admin"],
            "autonomous_execution": False,
        },
    )

    if approve:
        transition(run, RunStatus.APPROVED)
        transition(run, RunStatus.COMPLETED)
    else:
        transition(run, RunStatus.REJECTED)

    _refresh_metrics(db, run)
    db.flush()
    return proposal


# --- internal execution -----------------------------------------------------


def _execute(db: Session, run: WorkflowRun, *, replay: bool) -> None:
    transition(run, RunStatus.RUNNING)
    context: dict[str, Any] = {"replay": replay}

    handlers: dict[str, Callable[[Session, WorkflowRun, dict[str, Any]], dict[str, object]]] = {
        "fixture_loader": _tool_fixture_loader,
        "geo_validator": _tool_geo_validator,
        "provenance_recorder": _tool_provenance_recorder,
        "policy_evaluator": _tool_policy_evaluator,
        "allocation_planner": _tool_allocation_planner,
        "approval_gate": _tool_approval_gate,
    }

    for step_key, tool_name in WORKFLOW_STEPS:
        spec = resolve_tool(tool_name)
        handler = handlers[spec.name]
        succeeded = False
        for attempt in range(1, spec.max_attempts + 1):
            try:
                detail = handler(db, run, context)
            except ToolTimeoutError:
                _record_step(
                    db,
                    run,
                    step_key=step_key,
                    tool_name=spec.name,
                    attempt=attempt,
                    status=StepStatus.TIMED_OUT,
                    detail={"timeout_budget_seconds": spec.timeout_seconds},
                )
                if attempt == spec.max_attempts:
                    transition(run, RunStatus.DEAD_LETTER)
                    _add_disclosure(
                        run,
                        f"Step '{step_key}' exhausted {spec.max_attempts} attempts and "
                        "was dead-lettered; it can be replayed by a coordinator.",
                    )
                    _refresh_metrics(db, run)
                    db.flush()
                    return
                continue
            except StepValidationError as exc:
                _record_step(
                    db,
                    run,
                    step_key=step_key,
                    tool_name=spec.name,
                    attempt=attempt,
                    status=StepStatus.FAILED,
                    detail={"error_codes": exc.codes},
                )
                transition(run, RunStatus.FAILED)
                for code in exc.codes:
                    _add_disclosure(run, f"Rejected by validation: {code}")
                _refresh_metrics(db, run)
                db.flush()
                return
            else:
                _record_step(
                    db,
                    run,
                    step_key=step_key,
                    tool_name=spec.name,
                    attempt=attempt,
                    status=StepStatus.SUCCEEDED,
                    detail=detail,
                )
                succeeded = True
                break
        if not succeeded:  # pragma: no cover - defensive; loop always resolves
            raise RuntimeError("Step neither succeeded nor terminated the run.")

    transition(run, RunStatus.AWAITING_APPROVAL)
    _refresh_metrics(db, run)
    db.flush()


def _tool_fixture_loader(
    db: Session, run: WorkflowRun, context: dict[str, Any]
) -> dict[str, object]:
    scenario = fixtures.Scenario(run.scenario)
    fixture = fixtures.load_fixture(scenario)
    # Simulated transient upstream timeout, cleared on operator replay.
    if fixture["flags"]["simulate_timeout_ingest"] and not context["replay"]:
        raise ToolTimeoutError("Simulated fixture source timeout.")
    context["fixture"] = fixture
    context["as_of"] = datetime.fromisoformat(fixture["as_of"])
    return {
        "fixture_id": fixture["fixture_id"],
        "synthetic": True,
        "checksum_sha256": fixtures.fixture_checksum(fixture),
        "zone_count": len(fixture["zones_table"]),
    }


def _tool_geo_validator(
    db: Session, run: WorkflowRun, context: dict[str, Any]
) -> dict[str, object]:
    result = geo.validate_hazard_layer(context["fixture"]["hazard_geojson"], context["as_of"])
    if not result.ok:
        raise StepValidationError(result.errors)
    for warning in result.warnings:
        _add_disclosure(run, f"Geospatial disclosure: {warning}")
    return {"errors": 0, "warnings": result.warnings, "crs": "EPSG:4326 (RFC 7946 default)"}


def _tool_provenance_recorder(
    db: Session, run: WorkflowRun, context: dict[str, Any]
) -> dict[str, object]:
    fixture = context["fixture"]
    checksum = fixtures.fixture_checksum(fixture)
    provenance = FixtureProvenance(
        run_id=run.id,
        fixture_id=fixture["fixture_id"],
        source_label=fixture["source_label"],
        synthetic=bool(fixture["synthetic"]),
        license_note=fixture["license_note"],
        checksum_sha256=checksum,
        effective_at=datetime.fromisoformat(fixture["effective_at"]),
        retrieved_at=utcnow(),
    )
    db.add(provenance)
    return {
        "fixture_id": fixture["fixture_id"],
        "synthetic": True,
        "checksum_prefix": checksum[:12],
    }


def _tool_policy_evaluator(
    db: Session, run: WorkflowRun, context: dict[str, Any]
) -> dict[str, object]:
    checks = policy_service.evaluate_policy(context["fixture"], context["as_of"])
    run.policy_results = [check.as_dict() for check in checks]
    failed = [check.check for check in checks if not check.passed]
    if failed:
        raise StepValidationError([f"policy:{name}" for name in failed])

    for check in checks:
        if check.check == "prompt_injection_guard":
            markers = int(str(check.detail.get("suspicious_markers", 0)))
            if markers:
                _add_disclosure(
                    run,
                    f"Prompt-injection guard flagged {markers} suspicious marker(s) in "
                    "fixture text; the text was treated as data and could not alter "
                    "steps, tools, or policy.",
                )
        if check.check == "sensitive_data_guard":
            markers = int(str(check.detail.get("redacted_markers", 0)))
            if markers:
                _add_disclosure(
                    run,
                    f"Sensitive-data guard redacted {markers} marker(s); raw fixture "
                    "text is never stored or logged.",
                )
    return {
        "policy_version": run.policy_version,
        "checks_passed": len(checks),
        "checks_failed": 0,
    }


def _tool_allocation_planner(
    db: Session, run: WorkflowRun, context: dict[str, Any]
) -> dict[str, object]:
    fixture = context["fixture"]
    result = allocation_service.propose_allocation(
        fixture["zones_table"], fixture["inventory"], fixture["demand"]
    )
    proposal = AllocationProposal(
        run_id=run.id,
        status=ProposalStatus.PROPOSED,
        lines=[line.as_dict() for line in result.lines],
        unmet_demand=[line.as_dict() for line in result.unmet_demand],
    )
    db.add(proposal)
    context["allocation"] = result
    return {
        "allocated_units": result.allocated_units,
        "unmet_units": result.unmet_units,
        "line_count": len(result.lines),
        "heuristic": "greedy severity/population priority (no optimality guarantee)",
    }


def _tool_approval_gate(
    db: Session, run: WorkflowRun, context: dict[str, Any]
) -> dict[str, object]:
    return {
        "requires_role": ["coordinator", "admin"],
        "autonomous_execution": False,
        "decision_endpoint": "approval",
    }


def _record_step(
    db: Session,
    run: WorkflowRun,
    *,
    step_key: str,
    tool_name: str,
    attempt: int,
    status: StepStatus,
    detail: dict[str, object],
) -> None:
    next_seq = db.scalar(
        select(func.coalesce(func.max(WorkflowRunStep.seq), 0)).where(
            WorkflowRunStep.run_id == run.id
        )
    )
    db.add(
        WorkflowRunStep(
            run_id=run.id,
            seq=int(next_seq or 0) + 1,
            step_key=step_key,
            tool_name=tool_name,
            attempt=attempt,
            status=status,
            detail=detail,
        )
    )
    db.flush()


def _add_disclosure(run: WorkflowRun, message: str) -> None:
    disclosures = list(run.disclosures)
    if message not in disclosures:
        disclosures.append(message)
    run.disclosures = disclosures


def _refresh_metrics(db: Session, run: WorkflowRun) -> None:
    steps = db.scalars(
        select(WorkflowRunStep).where(WorkflowRunStep.run_id == run.id)
    ).all()
    retries = sum(1 for step in steps if step.attempt > 1)
    proposal = db.scalar(
        select(AllocationProposal).where(AllocationProposal.run_id == run.id)
    )
    allocated = (
        sum(int(str(line["quantity"])) for line in proposal.lines) if proposal else 0
    )
    unmet = (
        sum(int(str(line["quantity"])) for line in proposal.unmet_demand) if proposal else 0
    )
    checks = run.policy_results or []
    run.metrics = {
        "step_events": len(steps),
        "retries": retries,
        "duration_ticks": len(steps),
        "policy_checks_passed": sum(1 for check in checks if check.get("passed")),
        "policy_checks_failed": sum(1 for check in checks if not check.get("passed")),
        "allocated_units": allocated,
        "unmet_units": unmet,
        "replay_count": run.replay_count,
    }
