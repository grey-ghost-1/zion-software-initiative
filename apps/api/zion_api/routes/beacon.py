"""Beacon demonstration API routes.

All run access is organization-scoped through the caller's membership; a run
in another organization is indistinguishable from a missing run (404).
Approval and replay additionally require the coordinator or admin role.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from zion_api.core.errors import RunConflictError, RunNotFoundError
from zion_api.db.session import get_db
from zion_api.deps import get_membership_for_org, require_coordinator_or_admin
from zion_api.models.beacon import WorkflowRun
from zion_api.models.membership import Membership
from zion_api.models.organization import Organization
from zion_api.schemas.beacon import (
    ApprovalRequest,
    CapabilitiesResponse,
    PolicyCheckOut,
    ProposalOut,
    ProvenanceOut,
    RunDetailResponse,
    RunListResponse,
    RunStepOut,
    RunSummaryOut,
    StartRunRequest,
    StartRunResponse,
    ToolSpecOut,
    WorkflowStepOut,
)
from zion_api.services.audit import record_audit_event
from zion_api.services.beacon import engine
from zion_api.services.beacon.fixtures import Scenario
from zion_api.services.beacon.policy import POLICY_VERSION
from zion_api.services.beacon.tools import TOOL_REGISTRY

router = APIRouter(prefix="/beacon", tags=["beacon"])

_GUARDRAILS = [
    "All inputs are canned synthetic fixtures; no live weather, map, or model calls.",
    "Typed allowlisted tools only; no arbitrary tool names, URLs, code, or shell.",
    "Every allocation requires explicit human approval by a coordinator or admin.",
    "No autonomous purchasing, dispatch, beneficiary ranking, evacuation order, or public warning.",
    "Fixture text is treated as data; it cannot alter steps, tools, or policy.",
    "No raw fixture text or sensitive content is persisted or logged.",
]

_DISCLOSURE = (
    "Synthetic exploratory demonstration only. This is not an official hazard "
    "product and issues no warnings; consult official sources such as the "
    "National Weather Service for real conditions."
)


@router.get("/capabilities", response_model=CapabilitiesResponse)
def get_capabilities() -> CapabilitiesResponse:
    """Describe the one fixed demo workflow, its typed tools, and guardrails."""

    return CapabilitiesResponse(
        workflow_key=engine.WORKFLOW_KEY,
        workflow_version=engine.WORKFLOW_VERSION,
        workflow_name=engine.WORKFLOW_NAME,
        policy_version=POLICY_VERSION,
        steps=[
            WorkflowStepOut(step_key=step_key, tool=tool_name)
            for step_key, tool_name in (*engine.WORKFLOW_STEPS, engine.OUTCOME_STEP)
        ],
        tools=[
            ToolSpecOut(
                name=spec.name,
                description=spec.description,
                input_type=spec.input_type,
                output_type=spec.output_type,
                timeout_seconds=spec.timeout_seconds,
                max_attempts=spec.max_attempts,
            )
            for spec in TOOL_REGISTRY.values()
        ],
        scenarios=[scenario.value for scenario in Scenario],
        guardrails=_GUARDRAILS,
        disclosure=_DISCLOSURE,
    )


@router.post(
    "/organizations/{org_slug}/runs",
    response_model=StartRunResponse,
)
def start_run(
    payload: StartRunRequest,
    org_membership: tuple[Organization, Membership] = Depends(get_membership_for_org),
    db: Session = Depends(get_db),
) -> StartRunResponse:
    """Start one idempotent demonstration run from the canned fixture."""

    organization, membership = org_membership
    try:
        run, created = engine.start_run(
            db,
            organization_id=organization.id,
            user_id=membership.user_id,
            idempotency_key=payload.idempotency_key,
            scenario=payload.scenario,
        )
    except engine.IdempotencyConflict as exc:
        raise RunConflictError(str(exc)) from exc

    if created:
        record_audit_event(
            db,
            action="beacon.run_started",
            actor_user_id=membership.user_id,
            organization_id=organization.id,
            subject_type="beacon_run",
            subject_id=run.id,
            context={"scenario": run.scenario, "status": run.status.value},
        )
    db.commit()
    return StartRunResponse(created=created, run=_run_detail(db, run))


@router.get("/organizations/{org_slug}/runs", response_model=RunListResponse)
def list_runs(
    org_membership: tuple[Organization, Membership] = Depends(get_membership_for_org),
    db: Session = Depends(get_db),
) -> RunListResponse:
    """List this organization's demonstration runs, newest first."""

    organization, _ = org_membership
    runs = db.scalars(
        select(WorkflowRun)
        .where(WorkflowRun.organization_id == organization.id)
        .order_by(WorkflowRun.created_at.desc(), WorkflowRun.id)
    ).all()
    return RunListResponse(
        organization_slug=organization.slug,
        runs=[_run_summary(run) for run in runs],
    )


@router.get("/organizations/{org_slug}/runs/{run_id}", response_model=RunDetailResponse)
def get_run(
    run_id: str,
    org_membership: tuple[Organization, Membership] = Depends(get_membership_for_org),
    db: Session = Depends(get_db),
) -> RunDetailResponse:
    """Inspect one run: steps, policy results, provenance, proposal, metrics."""

    organization, _ = org_membership
    run = _get_org_run(db, organization, run_id)
    return _run_detail(db, run)


@router.post(
    "/organizations/{org_slug}/runs/{run_id}/approval",
    response_model=RunDetailResponse,
)
def decide_allocation(
    run_id: str,
    payload: ApprovalRequest,
    org_membership: tuple[Organization, Membership] = Depends(require_coordinator_or_admin),
    db: Session = Depends(get_db),
) -> RunDetailResponse:
    """Approve or reject the pending allocation proposal (coordinator/admin)."""

    organization, membership = org_membership
    run = _get_org_run(db, organization, run_id)
    try:
        engine.decide_allocation(
            db,
            run,
            decided_by_user_id=membership.user_id,
            approve=payload.decision == "approve",
            note=payload.note,
        )
    except engine.RunStateConflict as exc:
        raise RunConflictError(str(exc)) from exc

    record_audit_event(
        db,
        action=f"beacon.allocation_{payload.decision}d",
        actor_user_id=membership.user_id,
        organization_id=organization.id,
        subject_type="beacon_run",
        subject_id=run.id,
        context={"decision": payload.decision, "status": run.status.value},
    )
    db.commit()
    return _run_detail(db, run)


@router.post(
    "/organizations/{org_slug}/runs/{run_id}/replay",
    response_model=RunDetailResponse,
)
def replay_run(
    run_id: str,
    org_membership: tuple[Organization, Membership] = Depends(require_coordinator_or_admin),
    db: Session = Depends(get_db),
) -> RunDetailResponse:
    """Replay one dead-lettered run after simulated upstream recovery."""

    organization, membership = org_membership
    run = _get_org_run(db, organization, run_id)
    try:
        engine.replay_run(db, run)
    except engine.RunStateConflict as exc:
        raise RunConflictError(str(exc)) from exc

    record_audit_event(
        db,
        action="beacon.run_replayed",
        actor_user_id=membership.user_id,
        organization_id=organization.id,
        subject_type="beacon_run",
        subject_id=run.id,
        context={"replay_count": run.replay_count, "status": run.status.value},
    )
    db.commit()
    return _run_detail(db, run)


def _get_org_run(db: Session, organization: Organization, run_id: str) -> WorkflowRun:
    run = db.scalar(
        select(WorkflowRun).where(
            WorkflowRun.id == run_id,
            WorkflowRun.organization_id == organization.id,
        )
    )
    if run is None:
        raise RunNotFoundError("The run was not found.")
    return run


def _run_summary(run: WorkflowRun) -> RunSummaryOut:
    return RunSummaryOut(
        id=run.id,
        workflow_key=run.workflow_key,
        workflow_version=run.workflow_version,
        policy_version=run.policy_version,
        scenario=run.scenario,
        fixture_id=run.fixture_id,
        status=run.status.value,
        idempotency_key=run.idempotency_key,
        replay_count=run.replay_count,
        created_at=run.created_at,
    )


def _run_detail(db: Session, run: WorkflowRun) -> RunDetailResponse:
    db.refresh(run)
    summary = _run_summary(run)
    return RunDetailResponse(
        **summary.model_dump(),
        steps=[
            RunStepOut(
                seq=step.seq,
                step_key=step.step_key,
                tool_name=step.tool_name,
                attempt=step.attempt,
                status=step.status.value,
                detail=step.detail,
                created_at=step.created_at,
            )
            for step in run.steps
        ],
        policy_results=[
            PolicyCheckOut(
                check=str(item["check"]),
                passed=bool(item["passed"]),
                detail=dict(item["detail"]),  # type: ignore[call-overload]
            )
            for item in run.policy_results
        ],
        provenance=[
            ProvenanceOut(
                fixture_id=item.fixture_id,
                source_label=item.source_label,
                synthetic=item.synthetic,
                license_note=item.license_note,
                checksum_sha256=item.checksum_sha256,
                effective_at=item.effective_at,
                retrieved_at=item.retrieved_at,
            )
            for item in run.provenance
        ],
        proposal=(
            ProposalOut(
                id=run.proposal.id,
                status=run.proposal.status.value,
                lines=[line for line in run.proposal.lines],  # type: ignore[misc]
                unmet_demand=[line for line in run.proposal.unmet_demand],  # type: ignore[misc]
                decided_at=run.proposal.decided_at,
                decision_note=run.proposal.decision_note,
            )
            if run.proposal
            else None
        ),
        metrics=run.metrics,
        disclosures=run.disclosures,
    )
