"""Deterministic matching and transactional Harbor workflow operations."""

from __future__ import annotations

from typing import Any, cast

from sqlalchemy import CursorResult, func, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from zion_api.core.errors import HarborConflictError, HarborNotFoundError
from zion_api.core.security import utcnow
from zion_api.models.audit_event import AuditEvent
from zion_api.models.harbor import (
    AccessibilityRequirement,
    AccessibilityStatus,
    CapacityFreshness,
    HarborCapacity,
    HarborNeed,
    HarborPlan,
    HarborResource,
    HarborVolunteerAvailability,
    NeedStatus,
    PlanStatus,
    ResourceStatus,
    TriageDecision,
)
from zion_api.schemas.harbor import (
    HarborAuditItem,
    HarborAuditTimeline,
    HarborCapacityResponse,
    HarborMatch,
    HarborMetricsResponse,
    HarborNeedResponse,
    HarborPlanResponse,
    HarborResourceResponse,
    ScoreComponent,
)
from zion_api.services.audit import record_audit_event

SYNTHETIC_DISCLOSURE = (
    "Synthetic demonstration data only. It does not represent people, partners, "
    "confidential sites, current availability, or aid provision."
)


def need_response(need: HarborNeed) -> HarborNeedResponse:
    return HarborNeedResponse(
        id=need.id,
        request_ref=need.request_ref,
        category=need.category,
        zone=need.zone,
        quantity=need.quantity,
        eligibility=need.eligibility,
        accessibility_requirement=need.accessibility_requirement,
        urgency=need.urgency,
        status=need.status,
        triage_decision=need.triage_decision,
        triage_reason=need.triage_reason,
        created_at=need.created_at,
    )


def capacity_response(capacity: HarborCapacity | None) -> HarborCapacityResponse | None:
    if capacity is None:
        return None
    available = None
    if capacity.freshness == CapacityFreshness.CURRENT:
        available = capacity.total_units - capacity.reserved_units - capacity.fulfilled_units
    return HarborCapacityResponse(
        total_units=capacity.total_units,
        reserved_units=capacity.reserved_units,
        fulfilled_units=capacity.fulfilled_units,
        available_units=available,
        freshness=capacity.freshness,
    )


def resource_response(
    resource: HarborResource, capacity: HarborCapacity | None
) -> HarborResourceResponse:
    return HarborResourceResponse(
        id=resource.id,
        code=resource.code,
        name=resource.name,
        category=resource.category,
        zone=resource.zone,
        eligibility=resource.eligibility,
        accessibility=resource.accessibility,
        status=resource.status,
        capacity=capacity_response(capacity),
    )


def _component(rule: str, points: int, explanation: str) -> ScoreComponent:
    return ScoreComponent(rule=rule, points=points, explanation=explanation)


def _zone_points(need: HarborNeed, resource: HarborResource) -> int:
    if need.zone == resource.zone:
        return 20
    order = {"north": 0, "central": 1, "south": 2}
    return 12 if abs(order[need.zone.value] - order[resource.zone.value]) == 1 else 4


def calculate_match(
    need: HarborNeed,
    resource: HarborResource,
    capacity: HarborCapacity | None,
) -> HarborMatch:
    """Apply fixed, inspectable rules without protected traits or model calls."""

    components: list[ScoreComponent] = []
    rejected: list[str] = []
    uncertainty = ["Distance uses coarse synthetic zones only; no routing or geocoding is used."]

    if resource.category != need.category:
        rejected.append("category_mismatch")
    else:
        components.append(_component("need_category", 30, "Resource category matches the request."))

    eligibility_matches = (
        resource.eligibility == need.eligibility
        or resource.eligibility.value == "open_access"
    )
    if not eligibility_matches:
        rejected.append("eligibility_not_met")
    else:
        components.append(
            _component("eligibility", 15, "Controlled eligibility rules are compatible.")
        )

    zone_points = _zone_points(need, resource)
    components.append(
        _component(
            "coarse_zone",
            zone_points,
            "Same-zone resources score 20; adjacent 12; two zones away 4.",
        )
    )

    if resource.status != ResourceStatus.OPEN:
        rejected.append("resource_closed")
    else:
        components.append(_component("open_status", 10, "Resource is marked open."))

    if capacity is None:
        rejected.append("capacity_missing")
    elif capacity.freshness == CapacityFreshness.STALE:
        rejected.append("capacity_stale")
    elif capacity.freshness == CapacityFreshness.UNKNOWN:
        rejected.append("capacity_unknown")
    else:
        components.append(_component("capacity_freshness", 10, "Capacity is marked current."))
        available = capacity.total_units - capacity.reserved_units - capacity.fulfilled_units
        if available < need.quantity:
            rejected.append("capacity_insufficient")
        else:
            components.append(
                _component("available_capacity", 10, "Current capacity covers the request.")
            )

    if need.accessibility_requirement == AccessibilityRequirement.STEP_FREE:
        if resource.accessibility == AccessibilityStatus.LIMITED:
            rejected.append("step_free_access_not_available")
        elif resource.accessibility == AccessibilityStatus.UNKNOWN:
            uncertainty.append(
                "Step-free accessibility is unknown and requires coordinator confirmation."
            )
        else:
            components.append(
                _component("accessibility", 5, "Step-free access matches the request.")
            )
    else:
        components.append(
            _component("accessibility", 5, "No step-free requirement was specified.")
        )

    return HarborMatch(
        resource=resource_response(resource, capacity),
        score=None if rejected else sum(component.points for component in components),
        score_components=components,
        rejected_reasons=rejected,
        uncertainty=uncertainty,
    )


def calculate_matches(db: Session, need: HarborNeed) -> tuple[list[HarborMatch], list[HarborMatch]]:
    rows = db.execute(
        select(HarborResource, HarborCapacity)
        .outerjoin(HarborCapacity, HarborCapacity.resource_id == HarborResource.id)
        .where(HarborResource.organization_id == need.organization_id)
        .order_by(HarborResource.code)
    ).all()
    candidates = [calculate_match(need, resource, capacity) for resource, capacity in rows]
    matches = sorted(
        (candidate for candidate in candidates if not candidate.rejected_reasons),
        key=lambda candidate: (-(candidate.score or 0), candidate.resource.code),
    )
    rejected = [candidate for candidate in candidates if candidate.rejected_reasons]
    return matches, rejected


def get_need(db: Session, organization_id: str, need_id: str) -> HarborNeed:
    need = db.scalar(
        select(HarborNeed).where(
            HarborNeed.id == need_id, HarborNeed.organization_id == organization_id
        )
    )
    if need is None:
        raise HarborNotFoundError("The Harbor request was not found.")
    return need


def get_resource(db: Session, organization_id: str, resource_id: str) -> HarborResource:
    resource = db.scalar(
        select(HarborResource).where(
            HarborResource.id == resource_id,
            HarborResource.organization_id == organization_id,
        )
    )
    if resource is None:
        raise HarborNotFoundError("The Harbor resource was not found.")
    return resource


def propose_plan(
    db: Session,
    *,
    need: HarborNeed,
    resource: HarborResource,
    volunteer_availability_id: str,
    actor_user_id: str,
) -> HarborPlan:
    if need.status != NeedStatus.TRIAGED or need.triage_decision != TriageDecision.READY:
        raise HarborConflictError("Coordinator triage must mark the request ready first.")
    accepted, _ = calculate_matches(db, need)
    if resource.id not in {candidate.resource.id for candidate in accepted}:
        raise HarborConflictError("The resource is not currently an eligible match.")

    volunteer = db.scalar(
        select(HarborVolunteerAvailability).where(
            HarborVolunteerAvailability.id == volunteer_availability_id,
            HarborVolunteerAvailability.organization_id == need.organization_id,
            HarborVolunteerAvailability.category == need.category,
            HarborVolunteerAvailability.available.is_(True),
        )
    )
    if volunteer is None:
        raise HarborConflictError(
            "The selected synthetic volunteer availability is not eligible."
        )
    plan = HarborPlan(
        organization_id=need.organization_id,
        need_id=need.id,
        resource_id=resource.id,
        volunteer_availability_id=volunteer.id,
        quantity=need.quantity,
        status=PlanStatus.PROPOSED,
    )
    db.add(plan)
    need.status = NeedStatus.PROPOSED
    try:
        db.flush()
    except IntegrityError as exc:
        db.rollback()
        raise HarborConflictError("This request already has a Harbor plan.") from exc
    record_audit_event(
        db,
        action="harbor.plan_proposed",
        actor_user_id=actor_user_id,
        organization_id=need.organization_id,
        subject_type="harbor_need",
        subject_id=need.id,
        context={"plan_id": plan.id, "resource_id": resource.id},
    )
    db.commit()
    return plan


def _get_plan(db: Session, organization_id: str, plan_id: str) -> HarborPlan:
    plan = db.scalar(
        select(HarborPlan).where(
            HarborPlan.id == plan_id, HarborPlan.organization_id == organization_id
        )
    )
    if plan is None:
        raise HarborNotFoundError("The Harbor plan was not found.")
    return plan


def approve_plan(
    db: Session, *, organization_id: str, plan_id: str, actor_user_id: str
) -> HarborPlan:
    """Approve a plan and atomically reserve capacity without overbooking."""

    plan = _get_plan(db, organization_id, plan_id)
    if plan.status != PlanStatus.PROPOSED:
        raise HarborConflictError("Only a proposed plan can be approved.")
    resource = get_resource(db, organization_id, plan.resource_id)
    if resource.status != ResourceStatus.OPEN:
        raise HarborConflictError("Closed resources cannot accept reservations.")

    transition_at = utcnow()
    plan_claim = cast(
        CursorResult[Any],
        db.execute(
            update(HarborPlan)
            .where(
                HarborPlan.id == plan.id,
                HarborPlan.organization_id == organization_id,
                HarborPlan.status == PlanStatus.PROPOSED,
            )
            .values(status=PlanStatus.APPROVED, approved_at=transition_at)
            .execution_options(synchronize_session=False)
        ),
    )
    if plan_claim.rowcount != 1:
        db.rollback()
        raise HarborConflictError("Only a proposed plan can be approved.")

    capacity_update = cast(
        CursorResult[Any],
        db.execute(
            update(HarborCapacity)
            .where(
                HarborCapacity.resource_id == plan.resource_id,
                HarborCapacity.organization_id == organization_id,
                HarborCapacity.freshness == CapacityFreshness.CURRENT,
                HarborCapacity.reserved_units
                + HarborCapacity.fulfilled_units
                + plan.quantity
                <= HarborCapacity.total_units,
            )
            .values(reserved_units=HarborCapacity.reserved_units + plan.quantity)
        )
    )
    if capacity_update.rowcount != 1:
        db.rollback()
        raise HarborConflictError("Current capacity cannot cover this reservation.")

    need = get_need(db, organization_id, plan.need_id)
    need.status = NeedStatus.APPROVED
    record_audit_event(
        db,
        action="harbor.plan_approved_capacity_reserved",
        actor_user_id=actor_user_id,
        organization_id=organization_id,
        subject_type="harbor_need",
        subject_id=need.id,
        context={"plan_id": plan.id, "reserved_units": plan.quantity},
    )
    db.commit()
    db.refresh(plan)
    return plan


def fulfill_plan(
    db: Session, *, organization_id: str, plan_id: str, actor_user_id: str
) -> HarborPlan:
    plan = _get_plan(db, organization_id, plan_id)
    if plan.status != PlanStatus.APPROVED:
        raise HarborConflictError("Explicit approval is required before fulfillment.")
    transition_at = utcnow()
    plan_claim = cast(
        CursorResult[Any],
        db.execute(
            update(HarborPlan)
            .where(
                HarborPlan.id == plan.id,
                HarborPlan.organization_id == organization_id,
                HarborPlan.status == PlanStatus.APPROVED,
            )
            .values(status=PlanStatus.FULFILLED, fulfilled_at=transition_at)
            .execution_options(synchronize_session=False)
        ),
    )
    if plan_claim.rowcount != 1:
        db.rollback()
        raise HarborConflictError("Explicit approval is required before fulfillment.")

    capacity_update = cast(
        CursorResult[Any],
        db.execute(
            update(HarborCapacity)
            .where(
                HarborCapacity.resource_id == plan.resource_id,
                HarborCapacity.organization_id == organization_id,
                HarborCapacity.reserved_units >= plan.quantity,
            )
            .values(
                reserved_units=HarborCapacity.reserved_units - plan.quantity,
                fulfilled_units=HarborCapacity.fulfilled_units + plan.quantity,
            )
        )
    )
    if capacity_update.rowcount != 1:
        db.rollback()
        raise HarborConflictError("The reserved capacity is no longer valid.")

    need = get_need(db, organization_id, plan.need_id)
    need.status = NeedStatus.FULFILLED
    record_audit_event(
        db,
        action="harbor.plan_fulfilled",
        actor_user_id=actor_user_id,
        organization_id=organization_id,
        subject_type="harbor_need",
        subject_id=need.id,
        context={"plan_id": plan.id, "fulfilled_units": plan.quantity},
    )
    db.commit()
    db.refresh(plan)
    return plan


def plan_response(db: Session, plan: HarborPlan) -> HarborPlanResponse:
    need = get_need(db, plan.organization_id, plan.need_id)
    resource = get_resource(db, plan.organization_id, plan.resource_id)
    volunteer = db.get(HarborVolunteerAvailability, plan.volunteer_availability_id)
    if volunteer is None:
        raise HarborNotFoundError("The Harbor volunteer availability was not found.")
    return HarborPlanResponse(
        id=plan.id,
        need_id=need.id,
        request_ref=need.request_ref,
        resource_id=resource.id,
        resource_name=resource.name,
        resource_zone=resource.zone,
        category=need.category,
        quantity=plan.quantity,
        volunteer_code=volunteer.code,
        status=plan.status,
        proposed_at=plan.proposed_at,
        approved_at=plan.approved_at,
        fulfilled_at=plan.fulfilled_at,
    )


def audit_timeline(db: Session, organization_id: str, need_id: str) -> HarborAuditTimeline:
    get_need(db, organization_id, need_id)
    events = db.scalars(
        select(AuditEvent)
        .where(
            AuditEvent.organization_id == organization_id,
            AuditEvent.subject_type == "harbor_need",
            AuditEvent.subject_id == need_id,
        )
        .order_by(AuditEvent.occurred_at, AuditEvent.id)
    ).all()
    return HarborAuditTimeline(
        need_id=need_id,
        items=[
            HarborAuditItem(
                id=event.id,
                occurred_at=event.occurred_at,
                action=event.action,
                context=event.context,
            )
            for event in events
        ],
    )


def metrics(db: Session, organization_id: str) -> HarborMetricsResponse:
    total_requests = db.scalar(
        select(func.count()).select_from(HarborNeed).where(
            HarborNeed.organization_id == organization_id
        )
    ) or 0
    submitted = db.scalar(
        select(func.count()).select_from(HarborNeed).where(
            HarborNeed.organization_id == organization_id,
            HarborNeed.status == NeedStatus.SUBMITTED,
        )
    ) or 0
    fulfilled = db.scalar(
        select(func.count()).select_from(HarborNeed).where(
            HarborNeed.organization_id == organization_id,
            HarborNeed.status == NeedStatus.FULFILLED,
        )
    ) or 0
    active_plans = db.scalar(
        select(func.count()).select_from(HarborPlan).where(
            HarborPlan.organization_id == organization_id,
            HarborPlan.status != PlanStatus.FULFILLED,
        )
    ) or 0
    awaiting = db.scalar(
        select(func.count()).select_from(HarborPlan).where(
            HarborPlan.organization_id == organization_id,
            HarborPlan.status == PlanStatus.PROPOSED,
        )
    ) or 0
    available_resources = db.scalar(
        select(func.count())
        .select_from(HarborResource)
        .join(HarborCapacity, HarborCapacity.resource_id == HarborResource.id)
        .where(
            HarborResource.organization_id == organization_id,
            HarborResource.status == ResourceStatus.OPEN,
            HarborCapacity.freshness == CapacityFreshness.CURRENT,
            HarborCapacity.reserved_units + HarborCapacity.fulfilled_units
            < HarborCapacity.total_units,
        )
    ) or 0
    units = db.execute(
        select(
            func.coalesce(func.sum(HarborCapacity.reserved_units), 0),
            func.coalesce(func.sum(HarborCapacity.fulfilled_units), 0),
        ).where(HarborCapacity.organization_id == organization_id)
    ).one()
    return HarborMetricsResponse(
        total_requests=total_requests,
        submitted_requests=submitted,
        active_plans=active_plans,
        awaiting_approval=awaiting,
        fulfilled_requests=fulfilled,
        currently_available_resources=available_resources,
        reserved_units=units[0],
        fulfilled_units=units[1],
        synthetic_disclosure=SYNTHETIC_DISCLOSURE,
    )
