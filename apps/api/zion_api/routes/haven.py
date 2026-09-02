"""Haven routes: curated content, ephemeral navigation, and plan review.

Safety ordering is structural: the deterministic emergency/crisis check runs
before any database access, and emergency/crisis responses are built from
fixed constants so they succeed even when every downstream dependency fails.
"""

from __future__ import annotations

from collections.abc import Iterator
from datetime import date

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from zion_api.core.errors import AppError
from zion_api.core.security import utcnow
from zion_api.db.session import get_db
from zion_api.deps import get_membership_for_org
from zion_api.models.enums import Role
from zion_api.models.haven import (
    HavenGuidanceCard,
    HavenNavigationPlan,
    HavenPlanStatus,
    HavenResource,
    HavenRoutingOutcome,
)
from zion_api.models.membership import Membership
from zion_api.models.organization import Organization
from zion_api.schemas.haven import (
    EmergencyGuidance,
    GuidanceCardListResponse,
    GuidanceCardOut,
    NavigationRequest,
    NavigationResponse,
    PlanCloseResponse,
    PlanCreateResponse,
    PlanListResponse,
    PlanOut,
    PlanReviewRequest,
    PlanReviewResponse,
    ResourceListResponse,
    ResourceOut,
)
from zion_api.services.audit import record_audit_event
from zion_api.services.haven_content import card_violations
from zion_api.services.haven_routing import NEXT_STEPS, RESOURCE_KINDS, route_concern
from zion_api.services.haven_safety import (
    NO_MONITORING_NOTE,
    NON_DIAGNOSTIC_DISCLAIMER,
    SafetyEscalation,
    assess_safety,
    guidance_for,
)

router = APIRouter(prefix="/haven", tags=["haven"])


class HavenTemporarilyUnavailableError(AppError):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    code = "haven_temporarily_unavailable"


class HavenRoleDeniedError(AppError):
    status_code = status.HTTP_403_FORBIDDEN
    code = "role_denied"


class PlanNotFoundError(AppError):
    """Identical 404 whether the plan does not exist or belongs to another
    organization, so existence is never leaked across tenants."""

    status_code = status.HTTP_404_NOT_FOUND
    code = "plan_not_found"


def get_optional_db() -> Iterator[Session | None]:
    """Yield a database session, or ``None`` when the database is unavailable.

    The public navigation endpoint uses this so a database outage degrades to
    "resources temporarily unavailable" for routine concerns while emergency
    and crisis guidance keeps working unconditionally.
    """

    inner = get_db()
    try:
        db = next(inner)
    except Exception:  # pragma: no cover - exercised via dependency override
        yield None
        return
    try:
        yield db
    finally:
        inner.close()


def require_navigator_or_admin(
    org_membership: tuple[Organization, Membership] = Depends(get_membership_for_org),
) -> tuple[Organization, Membership]:
    """Plan review is restricted to navigator or admin roles, server-side."""

    _, membership = org_membership
    if membership.role not in (Role.NAVIGATOR, Role.ADMIN):
        raise HavenRoleDeniedError(
            "This action requires the navigator or admin role in this organization."
        )
    return org_membership


def _inactive_emergency() -> EmergencyGuidance:
    return EmergencyGuidance(active=False, no_monitoring_note=NO_MONITORING_NOTE)


def _active_emergency(escalation: SafetyEscalation) -> EmergencyGuidance:
    headline, steps = guidance_for(escalation)
    return EmergencyGuidance(
        active=True,
        kind=escalation.value,
        headline=headline,
        steps=list(steps),
        no_monitoring_note=NO_MONITORING_NOTE,
    )


def _resource_out(resource: HavenResource, today: date) -> ResourceOut:
    return ResourceOut(
        slug=resource.slug,
        name=resource.name,
        description=resource.description,
        url=resource.url,
        kind=resource.kind,
        jurisdiction=resource.jurisdiction,
        provenance=resource.provenance,
        source_mode=resource.source_mode,
        reviewed_on=resource.reviewed_on,
        retrieved_on=resource.retrieved_on,
        review_valid_until=resource.review_valid_until,
        freshness="current" if resource.review_valid_until >= today else "needs_review",
    )


def _card_out(card: HavenGuidanceCard) -> GuidanceCardOut:
    return GuidanceCardOut(
        slug=card.slug,
        category=card.category,
        title=card.title,
        original_text=card.original_text,
        plain_text=card.plain_text,
        source_name=card.source_name,
        source_url=card.source_url,
        jurisdiction=card.jurisdiction,
        reviewed_on=card.reviewed_on,
    )


def _servable_cards(db: Session) -> list[HavenGuidanceCard]:
    """Only cards that pass invariance and prohibited-content validation."""

    cards = db.scalars(select(HavenGuidanceCard).order_by(HavenGuidanceCard.slug)).all()
    return [card for card in cards if not card_violations(card.original_text, card.plain_text)]


def _routing_payload(
    db: Session | None, outcome: HavenRoutingOutcome, category_value: str
) -> tuple[list[ResourceOut], list[GuidanceCardOut]]:
    """Attach curated resources and cards; degrade to empty lists on failure."""

    if db is None:
        return [], []
    try:
        today = date.today()
        kinds = RESOURCE_KINDS[outcome]
        resources = db.scalars(
            select(HavenResource)
            .where(HavenResource.kind.in_(kinds), HavenResource.is_available.is_(True))
            .order_by(HavenResource.slug)
        ).all()
        cards = [card for card in _servable_cards(db) if card.category.value == category_value]
        return (
            [_resource_out(resource, today) for resource in resources],
            [_card_out(card) for card in cards],
        )
    except Exception:
        # Curated enrichment must never block the deterministic response.
        return [], []


def _build_navigation(
    payload: NavigationRequest, db: Session | None, *, stored: bool
) -> tuple[NavigationResponse, SafetyEscalation, bool]:
    """Deterministic safety check first, then routing, then enrichment."""

    assessment = assess_safety(
        immediate_danger=payload.immediate_danger,
        self_harm_risk=payload.self_harm_risk,
        concern_text=payload.concern_text,
    )
    outcome = route_concern(
        escalation=assessment.escalation,
        category=payload.concern_category,
        duration=payload.duration,
        severity=payload.severity,
    )

    if assessment.escalation is not SafetyEscalation.NONE:
        emergency = _active_emergency(assessment.escalation)
    else:
        emergency = _inactive_emergency()
        if db is None:
            raise HavenTemporarilyUnavailableError(
                "Curated guidance is temporarily unavailable. Please try again later. "
                "In an emergency, call 911; for crisis support, call or text 988."
            )

    resources, cards = _routing_payload(db, outcome, payload.concern_category.value)
    response = NavigationResponse(
        stored=stored,
        emergency=emergency,
        outcome=outcome,
        next_steps=list(NEXT_STEPS[outcome]),
        resources=resources,
        guidance_cards=cards,
        disclaimer=NON_DIAGNOSTIC_DISCLAIMER,
    )
    return response, assessment.escalation, assessment.crisis_language_detected


@router.get("/guidance-cards", response_model=GuidanceCardListResponse)
def list_guidance_cards(db: Session = Depends(get_db)) -> GuidanceCardListResponse:
    """List curated, validation-passing plain-language cards. Public."""

    return GuidanceCardListResponse(cards=[_card_out(card) for card in _servable_cards(db)])


@router.get("/resources", response_model=ResourceListResponse)
def list_resources(db: Session = Depends(get_db)) -> ResourceListResponse:
    """List curated outbound references with provenance and freshness. Public."""

    today = date.today()
    resources = db.scalars(
        select(HavenResource)
        .where(HavenResource.is_available.is_(True))
        .order_by(HavenResource.slug)
    ).all()
    return ResourceListResponse(
        resources=[_resource_out(resource, today) for resource in resources]
    )


@router.post("/navigations", response_model=NavigationResponse)
def submit_navigation(
    payload: NavigationRequest,
    db: Session | None = Depends(get_optional_db),
) -> NavigationResponse:
    """Ephemeral public demo navigation: nothing about the request is stored."""

    response, _, _ = _build_navigation(payload, db, stored=False)
    return response


def _plan_out(plan: HavenNavigationPlan, organization_slug: str) -> PlanOut:
    return PlanOut(
        id=plan.id,
        organization_slug=organization_slug,
        synthetic=plan.synthetic,
        concern_category=plan.concern_category,
        duration=plan.duration,
        severity=plan.severity,
        immediate_danger=plan.immediate_danger,
        self_harm_risk=plan.self_harm_risk,
        crisis_language_detected=plan.crisis_language_detected,
        routed_outcome=plan.routed_outcome,
        status=plan.status,
        review_reason_code=plan.review_reason_code,
        created_at=plan.created_at,
        reviewed_at=plan.reviewed_at,
        closed_at=plan.closed_at,
    )


def _get_org_plan(db: Session, organization: Organization, plan_id: str) -> HavenNavigationPlan:
    plan = db.scalar(
        select(HavenNavigationPlan).where(
            HavenNavigationPlan.id == plan_id,
            HavenNavigationPlan.organization_id == organization.id,
        )
    )
    if plan is None:
        raise PlanNotFoundError("The navigation plan was not found.")
    return plan


@router.post(
    "/organizations/{org_slug}/plans",
    response_model=PlanCreateResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_plan(
    payload: NavigationRequest,
    org_membership: tuple[Organization, Membership] = Depends(require_navigator_or_admin),
    db: Session = Depends(get_db),
) -> PlanCreateResponse:
    """Create one synthetic, organization-scoped plan (enums and flags only)."""

    organization, membership = org_membership
    navigation, escalation, crisis_detected = _build_navigation(payload, db, stored=True)

    plan = HavenNavigationPlan(
        organization_id=organization.id,
        created_by_user_id=membership.user_id,
        concern_category=payload.concern_category,
        duration=payload.duration,
        severity=payload.severity,
        immediate_danger=payload.immediate_danger,
        self_harm_risk=payload.self_harm_risk,
        crisis_language_detected=crisis_detected,
        routed_outcome=navigation.outcome,
    )
    db.add(plan)
    db.flush()
    record_audit_event(
        db,
        action="haven.plan_created",
        actor_user_id=membership.user_id,
        organization_id=organization.id,
        subject_type="haven_navigation_plan",
        subject_id=plan.id,
        context={
            "routed_outcome": navigation.outcome.value,
            "escalated": escalation is not SafetyEscalation.NONE,
        },
    )
    db.commit()

    return PlanCreateResponse(plan=_plan_out(plan, organization.slug), navigation=navigation)


@router.get("/organizations/{org_slug}/plans", response_model=PlanListResponse)
def list_plans(
    org_membership: tuple[Organization, Membership] = Depends(require_navigator_or_admin),
    db: Session = Depends(get_db),
) -> PlanListResponse:
    """List this organization's synthetic plans only."""

    organization, _ = org_membership
    plans = db.scalars(
        select(HavenNavigationPlan)
        .where(HavenNavigationPlan.organization_id == organization.id)
        .order_by(HavenNavigationPlan.created_at.desc(), HavenNavigationPlan.id)
    ).all()
    return PlanListResponse(
        organization_slug=organization.slug,
        plans=[_plan_out(plan, organization.slug) for plan in plans],
    )


@router.post(
    "/organizations/{org_slug}/plans/{plan_id}/review",
    response_model=PlanReviewResponse,
)
def review_plan(
    plan_id: str,
    payload: PlanReviewRequest,
    org_membership: tuple[Organization, Membership] = Depends(require_navigator_or_admin),
    db: Session = Depends(get_db),
) -> PlanReviewResponse:
    """Annotate a plan with one controlled reason code. No free text."""

    organization, membership = org_membership
    plan = _get_org_plan(db, organization, plan_id)

    plan.review_reason_code = payload.reason_code
    plan.reviewed_by_user_id = membership.user_id
    plan.reviewed_at = utcnow()
    if plan.status is HavenPlanStatus.OPEN:
        plan.status = HavenPlanStatus.REVIEWED

    record_audit_event(
        db,
        action="haven.plan_reviewed",
        actor_user_id=membership.user_id,
        organization_id=organization.id,
        subject_type="haven_navigation_plan",
        subject_id=plan.id,
        context={"reason_code": payload.reason_code.value},
    )
    db.commit()
    return PlanReviewResponse(plan=_plan_out(plan, organization.slug))


@router.post(
    "/organizations/{org_slug}/plans/{plan_id}/close",
    response_model=PlanCloseResponse,
)
def close_plan(
    plan_id: str,
    org_membership: tuple[Organization, Membership] = Depends(require_navigator_or_admin),
    db: Session = Depends(get_db),
) -> PlanCloseResponse:
    """Close a plan; writes an audit event."""

    organization, membership = org_membership
    plan = _get_org_plan(db, organization, plan_id)

    plan.status = HavenPlanStatus.CLOSED
    plan.closed_at = utcnow()

    record_audit_event(
        db,
        action="haven.plan_closed",
        actor_user_id=membership.user_id,
        organization_id=organization.id,
        subject_type="haven_navigation_plan",
        subject_id=plan.id,
        context={"final_status": plan.status.value},
    )
    db.commit()
    return PlanCloseResponse(plan=_plan_out(plan, organization.slug))
