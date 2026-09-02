"""Typed public contracts for the synthetic Harbor demonstration."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from zion_api.models.harbor import (
    AccessibilityRequirement,
    AccessibilityStatus,
    CapacityFreshness,
    Eligibility,
    HarborZone,
    NeedCategory,
    NeedStatus,
    NeedUrgency,
    PlanStatus,
    ResourceStatus,
    TriageDecision,
    TriageReason,
)


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class HarborNeedCreate(StrictModel):
    request_ref: str = Field(pattern=r"^DEMO-[A-Z0-9-]{3,20}$", max_length=25)
    category: NeedCategory
    zone: HarborZone
    quantity: int = Field(ge=1, le=8)
    eligibility: Eligibility
    accessibility_requirement: AccessibilityRequirement
    urgency: NeedUrgency


class HarborNeedResponse(StrictModel):
    id: str
    request_ref: str
    category: NeedCategory
    zone: HarborZone
    quantity: int
    eligibility: Eligibility
    accessibility_requirement: AccessibilityRequirement
    urgency: NeedUrgency
    status: NeedStatus
    triage_decision: TriageDecision | None
    triage_reason: TriageReason | None
    created_at: datetime
    synthetic: bool = True


class HarborNeedList(StrictModel):
    items: list[HarborNeedResponse]
    synthetic_disclosure: str


class HarborCapacityResponse(StrictModel):
    total_units: int
    reserved_units: int
    fulfilled_units: int
    available_units: int | None
    freshness: CapacityFreshness


class HarborResourceResponse(StrictModel):
    id: str
    code: str
    name: str
    category: NeedCategory
    zone: HarborZone
    eligibility: Eligibility
    accessibility: AccessibilityStatus
    status: ResourceStatus
    capacity: HarborCapacityResponse | None
    synthetic: bool = True


class HarborResourceList(StrictModel):
    items: list[HarborResourceResponse]
    synthetic_disclosure: str


class ScoreComponent(StrictModel):
    rule: str
    points: int
    explanation: str


class HarborMatch(StrictModel):
    resource: HarborResourceResponse
    score: int | None
    score_components: list[ScoreComponent]
    rejected_reasons: list[str]
    uncertainty: list[str]


class HarborMatchResponse(StrictModel):
    need: HarborNeedResponse
    matches: list[HarborMatch]
    rejected: list[HarborMatch]
    scoring_notice: str
    protected_traits_used: bool = False


class HarborTriageRequest(StrictModel):
    decision: TriageDecision
    reason: TriageReason
    selected_resource_id: str | None = Field(default=None, max_length=36)


class HarborPlanProposal(StrictModel):
    resource_id: str = Field(max_length=36)
    volunteer_availability_id: str = Field(max_length=36)


class HarborVolunteerAvailabilityResponse(StrictModel):
    id: str
    code: str
    zone: HarborZone
    category: NeedCategory
    available: bool


class HarborVolunteerAvailabilityList(StrictModel):
    items: list[HarborVolunteerAvailabilityResponse]
    selection_notice: str


class HarborPlanResponse(StrictModel):
    id: str
    need_id: str
    request_ref: str
    resource_id: str
    resource_name: str
    resource_zone: HarborZone
    category: NeedCategory
    quantity: int
    volunteer_code: str
    status: PlanStatus
    proposed_at: datetime
    approved_at: datetime | None
    fulfilled_at: datetime | None
    synthetic: bool = True


class HarborVolunteerPlanList(StrictModel):
    items: list[HarborPlanResponse]
    scope_notice: str


class HarborAuditItem(StrictModel):
    id: str
    occurred_at: datetime
    action: str
    context: dict[str, object]


class HarborAuditTimeline(StrictModel):
    need_id: str
    items: list[HarborAuditItem]


class HarborMetricsResponse(StrictModel):
    total_requests: int
    submitted_requests: int
    active_plans: int
    awaiting_approval: int
    fulfilled_requests: int
    currently_available_resources: int
    reserved_units: int
    fulfilled_units: int
    synthetic_disclosure: str
