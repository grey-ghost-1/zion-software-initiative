"""Typed, allowlisted tool registry for the Beacon workflow.

The registry is a closed, code-defined set. Fixture data, API callers, and
stored workflow definitions can never add a tool: any tool name outside this
registry is rejected before execution. There is deliberately no tool for
purchasing, dispatch, beneficiary ranking, evacuation orders, public warnings,
shell access, or arbitrary URLs/code.
"""

from __future__ import annotations

from dataclasses import dataclass


class OutOfPolicyToolError(RuntimeError):
    """Raised when a workflow step names a tool outside the typed registry."""


class ToolTimeoutError(RuntimeError):
    """Raised when a tool exceeds its declared (simulated) timeout budget."""


class StepValidationError(RuntimeError):
    """Raised when a step's typed validation rejects its input or output."""

    def __init__(self, codes: list[str]) -> None:
        super().__init__("; ".join(codes))
        self.codes = codes


@dataclass(frozen=True)
class ToolSpec:
    """Metadata contract for one allowlisted tool."""

    name: str
    description: str
    input_type: str
    output_type: str
    timeout_seconds: int
    max_attempts: int


TOOL_REGISTRY: dict[str, ToolSpec] = {
    spec.name: spec
    for spec in (
        ToolSpec(
            name="fixture_loader",
            description="Load one canned synthetic hazard fixture by allowlisted scenario.",
            input_type="Scenario",
            output_type="HazardFixture",
            timeout_seconds=2,
            max_attempts=3,
        ),
        ToolSpec(
            name="geo_validator",
            description="Validate CRS, geometry, coordinate ranges, and observation freshness.",
            input_type="HazardFixture",
            output_type="GeoValidationResult",
            timeout_seconds=2,
            max_attempts=1,
        ),
        ToolSpec(
            name="provenance_recorder",
            description="Record fixture source, license, checksum, and retrieval/effective time.",
            input_type="HazardFixture",
            output_type="FixtureProvenance",
            timeout_seconds=2,
            max_attempts=1,
        ),
        ToolSpec(
            name="policy_evaluator",
            description="Evaluate versioned policy checks and content guards over the fixture.",
            input_type="HazardFixture",
            output_type="PolicyCheckList",
            timeout_seconds=2,
            max_attempts=1,
        ),
        ToolSpec(
            name="allocation_planner",
            description="Propose a deterministic, explainable synthetic supply allocation.",
            input_type="ZonesInventoryDemand",
            output_type="AllocationResult",
            timeout_seconds=2,
            max_attempts=1,
        ),
        ToolSpec(
            name="approval_gate",
            description="Pause the run until a coordinator or admin approves or rejects.",
            input_type="AllocationResult",
            output_type="ApprovalRequest",
            timeout_seconds=2,
            max_attempts=1,
        ),
        ToolSpec(
            name="outcome_recorder",
            description="Record the human decision and final run outcome.",
            input_type="ApprovalDecision",
            output_type="RunOutcome",
            timeout_seconds=2,
            max_attempts=1,
        ),
    )
}


def resolve_tool(name: str) -> ToolSpec:
    """Return the spec for an allowlisted tool, or reject anything else."""

    spec = TOOL_REGISTRY.get(name)
    if spec is None:
        raise OutOfPolicyToolError(f"Tool '{name}' is not in the typed allowlist.")
    return spec
