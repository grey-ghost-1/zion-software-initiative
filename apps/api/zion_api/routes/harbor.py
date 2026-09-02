"""Organization-scoped endpoints for the synthetic Harbor vertical slice."""

from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from zion_api.core.errors import HarborConflictError
from zion_api.db.session import get_db
from zion_api.deps import (
    require_harbor_coordinator,
    require_harbor_viewer,
    require_harbor_volunteer,
)
from zion_api.models.harbor import (
    HarborCapacity,
    HarborNeed,
    HarborPlan,
    HarborResource,
    HarborVolunteerAvailability,
    NeedStatus,
    TriageDecision,
)
from zion_api.models.membership import Membership
from zion_api.models.organization import Organization
from zion_api.schemas.harbor import (
    HarborAuditTimeline,
    HarborMatchResponse,
    HarborMetricsResponse,
    HarborNeedCreate,
    HarborNeedList,
    HarborNeedResponse,
    HarborPlanProposal,
    HarborPlanResponse,
    HarborResourceList,
    HarborResourceResponse,
    HarborTriageRequest,
    HarborVolunteerAvailabilityList,
    HarborVolunteerAvailabilityResponse,
    HarborVolunteerPlanList,
)
from zion_api.services.audit import record_audit_event
from zion_api.services.harbor import (
    SYNTHETIC_DISCLOSURE,
    approve_plan,
    audit_timeline,
    calculate_matches,
    fulfill_plan,
    get_need,
    get_resource,
    metrics,
    need_response,
    plan_response,
    propose_plan,
    resource_response,
)

router = APIRouter(prefix="/harbor/{org_slug}", tags=["harbor"])


@router.get("/needs", response_model=HarborNeedList)
def list_needs(
    org_membership: tuple[Organization, Membership] = Depends(require_harbor_viewer),
    db: Session = Depends(get_db),
) -> HarborNeedList:
    organization, _ = org_membership
    needs = db.scalars(
        select(HarborNeed)
        .where(HarborNeed.organization_id == organization.id)
        .order_by(HarborNeed.request_ref)
    ).all()
    return HarborNeedList(
        items=[need_response(need) for need in needs],
        synthetic_disclosure=SYNTHETIC_DISCLOSURE,
    )


@router.post("/needs", response_model=HarborNeedResponse, status_code=status.HTTP_201_CREATED)
def create_need(
    payload: HarborNeedCreate,
    org_membership: tuple[Organization, Membership] = Depends(require_harbor_coordinator),
    db: Session = Depends(get_db),
) -> HarborNeedResponse:
    organization, membership = org_membership
    need = HarborNeed(organization_id=organization.id, **payload.model_dump())
    db.add(need)
    try:
        db.flush()
    except IntegrityError as exc:
        db.rollback()
        raise HarborConflictError("That synthetic request reference already exists.") from exc
    record_audit_event(
        db,
        action="harbor.need_created",
        actor_user_id=membership.user_id,
        organization_id=organization.id,
        subject_type="harbor_need",
        subject_id=need.id,
        context={"request_ref": need.request_ref},
    )
    db.commit()
    return need_response(need)


@router.get("/needs/{need_id}", response_model=HarborNeedResponse)
def detail_need(
    need_id: str,
    org_membership: tuple[Organization, Membership] = Depends(require_harbor_viewer),
    db: Session = Depends(get_db),
) -> HarborNeedResponse:
    organization, _ = org_membership
    return need_response(get_need(db, organization.id, need_id))


@router.get("/resources", response_model=HarborResourceList)
def list_resources(
    org_membership: tuple[Organization, Membership] = Depends(require_harbor_viewer),
    db: Session = Depends(get_db),
) -> HarborResourceList:
    organization, _ = org_membership
    rows = db.execute(
        select(HarborResource, HarborCapacity)
        .outerjoin(HarborCapacity, HarborCapacity.resource_id == HarborResource.id)
        .where(HarborResource.organization_id == organization.id)
        .order_by(HarborResource.code)
    ).all()
    return HarborResourceList(
        items=[resource_response(resource, capacity) for resource, capacity in rows],
        synthetic_disclosure=SYNTHETIC_DISCLOSURE,
    )


@router.get("/resources/{resource_id}", response_model=HarborResourceResponse)
def detail_resource(
    resource_id: str,
    org_membership: tuple[Organization, Membership] = Depends(require_harbor_viewer),
    db: Session = Depends(get_db),
) -> HarborResourceResponse:
    organization, _ = org_membership
    resource = get_resource(db, organization.id, resource_id)
    capacity = db.get(HarborCapacity, resource.id)
    return resource_response(resource, capacity)


@router.get("/needs/{need_id}/matches", response_model=HarborMatchResponse)
def explain_matches(
    need_id: str,
    org_membership: tuple[Organization, Membership] = Depends(require_harbor_viewer),
    db: Session = Depends(get_db),
) -> HarborMatchResponse:
    organization, _ = org_membership
    need = get_need(db, organization.id, need_id)
    matches, rejected = calculate_matches(db, need)
    return HarborMatchResponse(
        need=need_response(need),
        matches=matches,
        rejected=rejected,
        scoring_notice=(
            "Deterministic demonstration rules only. Scores compare category, controlled "
            "eligibility, coarse zone, open status, capacity freshness and availability, "
            "and accessibility; a coordinator makes every decision."
        ),
    )


@router.post("/needs/{need_id}/triage", response_model=HarborNeedResponse)
def triage_need(
    need_id: str,
    payload: HarborTriageRequest,
    org_membership: tuple[Organization, Membership] = Depends(require_harbor_coordinator),
    db: Session = Depends(get_db),
) -> HarborNeedResponse:
    organization, membership = org_membership
    need = get_need(db, organization.id, need_id)
    if need.status not in {NeedStatus.SUBMITTED, NeedStatus.TRIAGED, NeedStatus.DEFERRED}:
        raise HarborConflictError("This request can no longer be triaged.")
    if payload.selected_resource_id is not None:
        get_resource(db, organization.id, payload.selected_resource_id)
    need.triage_decision = payload.decision
    need.triage_reason = payload.reason
    need.status = (
        NeedStatus.TRIAGED if payload.decision == TriageDecision.READY else NeedStatus.DEFERRED
    )
    context: dict[str, object] = {
        "decision": payload.decision.value,
        "reason": payload.reason.value,
    }
    if payload.selected_resource_id is not None:
        context["selected_resource_id"] = payload.selected_resource_id
    record_audit_event(
        db,
        action="harbor.need_triaged",
        actor_user_id=membership.user_id,
        organization_id=organization.id,
        subject_type="harbor_need",
        subject_id=need.id,
        context=context,
    )
    db.commit()
    return need_response(need)


@router.post(
    "/needs/{need_id}/plans",
    response_model=HarborPlanResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_plan(
    need_id: str,
    payload: HarborPlanProposal,
    org_membership: tuple[Organization, Membership] = Depends(require_harbor_coordinator),
    db: Session = Depends(get_db),
) -> HarborPlanResponse:
    organization, membership = org_membership
    need = get_need(db, organization.id, need_id)
    resource = get_resource(db, organization.id, payload.resource_id)
    plan = propose_plan(
        db,
        need=need,
        resource=resource,
        volunteer_availability_id=payload.volunteer_availability_id,
        actor_user_id=membership.user_id,
    )
    return plan_response(db, plan)


@router.get("/volunteer-availability", response_model=HarborVolunteerAvailabilityList)
def volunteer_availability(
    org_membership: tuple[Organization, Membership] = Depends(require_harbor_coordinator),
    db: Session = Depends(get_db),
) -> HarborVolunteerAvailabilityList:
    organization, _ = org_membership
    rows = db.scalars(
        select(HarborVolunteerAvailability)
        .where(HarborVolunteerAvailability.organization_id == organization.id)
        .order_by(HarborVolunteerAvailability.code)
    ).all()
    return HarborVolunteerAvailabilityList(
        items=[
            HarborVolunteerAvailabilityResponse(
                id=row.id,
                code=row.code,
                zone=row.zone,
                category=row.category,
                available=row.available,
            )
            for row in rows
        ],
        selection_notice=(
            "A coordinator must explicitly choose one eligible synthetic availability."
        ),
    )


@router.post("/plans/{plan_id}/approve", response_model=HarborPlanResponse)
def approve(
    plan_id: str,
    org_membership: tuple[Organization, Membership] = Depends(require_harbor_coordinator),
    db: Session = Depends(get_db),
) -> HarborPlanResponse:
    organization, membership = org_membership
    plan = approve_plan(
        db, organization_id=organization.id, plan_id=plan_id, actor_user_id=membership.user_id
    )
    return plan_response(db, plan)


@router.post("/plans/{plan_id}/fulfill", response_model=HarborPlanResponse)
def fulfill(
    plan_id: str,
    org_membership: tuple[Organization, Membership] = Depends(require_harbor_coordinator),
    db: Session = Depends(get_db),
) -> HarborPlanResponse:
    organization, membership = org_membership
    plan = fulfill_plan(
        db, organization_id=organization.id, plan_id=plan_id, actor_user_id=membership.user_id
    )
    return plan_response(db, plan)


@router.get("/volunteer-plans", response_model=HarborVolunteerPlanList)
def volunteer_plans(
    org_membership: tuple[Organization, Membership] = Depends(require_harbor_volunteer),
    db: Session = Depends(get_db),
) -> HarborVolunteerPlanList:
    organization, membership = org_membership
    query = (
        select(HarborPlan)
        .join(
            HarborVolunteerAvailability,
            HarborVolunteerAvailability.id == HarborPlan.volunteer_availability_id,
        )
        .where(HarborPlan.organization_id == organization.id)
    )
    if membership.role.value == "volunteer":
        query = query.where(HarborVolunteerAvailability.user_id == membership.user_id)
    plans = db.scalars(query.order_by(HarborPlan.proposed_at)).all()
    return HarborVolunteerPlanList(
        items=[plan_response(db, plan) for plan in plans],
        scope_notice="Only fields needed for this synthetic assignment are returned.",
    )


@router.get("/needs/{need_id}/audit", response_model=HarborAuditTimeline)
def need_audit(
    need_id: str,
    org_membership: tuple[Organization, Membership] = Depends(require_harbor_viewer),
    db: Session = Depends(get_db),
) -> HarborAuditTimeline:
    organization, _ = org_membership
    return audit_timeline(db, organization.id, need_id)


@router.get("/metrics", response_model=HarborMetricsResponse)
def summary_metrics(
    org_membership: tuple[Organization, Membership] = Depends(require_harbor_viewer),
    db: Session = Depends(get_db),
) -> HarborMetricsResponse:
    organization, _ = org_membership
    return metrics(db, organization.id)
