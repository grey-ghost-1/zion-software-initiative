"""Pydantic schemas for the Beacon demonstration API."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from zion_api.services.beacon.fixtures import Scenario


class ToolSpecOut(BaseModel):
    name: str
    description: str
    input_type: str
    output_type: str
    timeout_seconds: int
    max_attempts: int


class WorkflowStepOut(BaseModel):
    step_key: str
    tool: str


class CapabilitiesResponse(BaseModel):
    workflow_key: str
    workflow_version: str
    workflow_name: str
    policy_version: str
    steps: list[WorkflowStepOut]
    tools: list[ToolSpecOut]
    scenarios: list[str]
    guardrails: list[str]
    disclosure: str


class StartRunRequest(BaseModel):
    idempotency_key: str = Field(min_length=1, max_length=100)
    scenario: Scenario = Scenario.DEFAULT


class RunStepOut(BaseModel):
    seq: int
    step_key: str
    tool_name: str
    attempt: int
    status: str
    detail: dict[str, object]
    created_at: datetime


class PolicyCheckOut(BaseModel):
    check: str
    passed: bool
    detail: dict[str, object]


class ProvenanceOut(BaseModel):
    fixture_id: str
    source_label: str
    synthetic: bool
    license_note: str
    checksum_sha256: str
    effective_at: datetime
    retrieved_at: datetime


class AllocationLineOut(BaseModel):
    zone_id: str
    item: str
    quantity: int
    reason: str


class ProposalOut(BaseModel):
    id: str
    status: str
    lines: list[AllocationLineOut]
    unmet_demand: list[AllocationLineOut]
    decided_at: datetime | None
    decision_note: str | None


class RunSummaryOut(BaseModel):
    id: str
    workflow_key: str
    workflow_version: str
    policy_version: str
    scenario: str
    fixture_id: str
    status: str
    idempotency_key: str
    replay_count: int
    created_at: datetime


class RunDetailResponse(RunSummaryOut):
    steps: list[RunStepOut]
    policy_results: list[PolicyCheckOut]
    provenance: list[ProvenanceOut]
    proposal: ProposalOut | None
    metrics: dict[str, object]
    disclosures: list[str]


class StartRunResponse(BaseModel):
    created: bool
    run: RunDetailResponse


class RunListResponse(BaseModel):
    organization_slug: str
    runs: list[RunSummaryOut]


class ApprovalRequest(BaseModel):
    decision: Literal["approve", "reject"]
    note: str | None = Field(default=None, max_length=500)
