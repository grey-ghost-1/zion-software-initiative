"""Typed request/response schemas for the Haven demonstration module.

Requests accept only controlled enums, booleans, and one short bounded text
field that is used for the deterministic safety check and never persisted.
"""

from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, Field

from zion_api.models.haven import (
    HavenConcernCategory,
    HavenConcernDuration,
    HavenPlanStatus,
    HavenProvenance,
    HavenResourceKind,
    HavenReviewReasonCode,
    HavenRoutingOutcome,
    HavenSeverity,
    HavenSourceMode,
)


class NavigationRequest(BaseModel):
    """A bounded, synthetic concern submission. No identifying fields exist."""

    concern_category: HavenConcernCategory
    duration: HavenConcernDuration
    severity: HavenSeverity
    immediate_danger: bool = False
    self_harm_risk: bool = False
    concern_text: str | None = Field(
        default=None,
        max_length=280,
        description=(
            "Optional short synthetic text, scanned by the deterministic safety "
            "check and then discarded. Never stored or logged."
        ),
    )


class PlanReviewRequest(BaseModel):
    reason_code: HavenReviewReasonCode


class EmergencyGuidance(BaseModel):
    active: bool
    kind: str | None = None
    headline: str | None = None
    steps: list[str] = Field(default_factory=list)
    no_monitoring_note: str


class ResourceOut(BaseModel):
    slug: str
    name: str
    description: str
    url: str
    kind: HavenResourceKind
    jurisdiction: str
    provenance: HavenProvenance
    source_mode: HavenSourceMode
    reviewed_on: date
    retrieved_on: date
    review_valid_until: date
    freshness: str


class ResourceListResponse(BaseModel):
    resources: list[ResourceOut]


class GuidanceCardOut(BaseModel):
    slug: str
    category: HavenConcernCategory
    title: str
    original_text: str
    plain_text: str
    source_name: str
    source_url: str
    jurisdiction: str
    reviewed_on: date


class GuidanceCardListResponse(BaseModel):
    cards: list[GuidanceCardOut]


class NavigationResponse(BaseModel):
    synthetic: bool = True
    stored: bool
    emergency: EmergencyGuidance
    outcome: HavenRoutingOutcome
    next_steps: list[str]
    resources: list[ResourceOut]
    guidance_cards: list[GuidanceCardOut]
    disclaimer: str


class PlanOut(BaseModel):
    id: str
    organization_slug: str
    synthetic: bool
    concern_category: HavenConcernCategory
    duration: HavenConcernDuration
    severity: HavenSeverity
    immediate_danger: bool
    self_harm_risk: bool
    crisis_language_detected: bool
    routed_outcome: HavenRoutingOutcome
    status: HavenPlanStatus
    review_reason_code: HavenReviewReasonCode | None
    created_at: datetime
    reviewed_at: datetime | None
    closed_at: datetime | None


class PlanCreateResponse(BaseModel):
    plan: PlanOut
    navigation: NavigationResponse


class PlanListResponse(BaseModel):
    organization_slug: str
    plans: list[PlanOut]


class PlanReviewResponse(BaseModel):
    plan: PlanOut


class PlanCloseResponse(BaseModel):
    plan: PlanOut
