"""Shared enumerations for the Zion schema."""

from __future__ import annotations

import enum


class Role(enum.StrEnum):
    """Reusable membership roles.

    Only ``admin`` is enforced by any endpoint in this foundation layer. The
    remaining roles exist so later product modules can reuse one shared role
    vocabulary instead of each defining its own.
    """

    VISITOR = "visitor"
    COORDINATOR = "coordinator"
    NAVIGATOR = "navigator"
    VOLUNTEER = "volunteer"
    ADMIN = "admin"


class RunStatus(enum.StrEnum):
    """Lifecycle states of one Beacon workflow run.

    The allowed transitions form a fixed state machine enforced by the
    engine (`zion_api.services.beacon.engine.ALLOWED_TRANSITIONS`); nothing
    in fixture data can add states or transitions.
    """

    RECEIVED = "received"
    RUNNING = "running"
    AWAITING_APPROVAL = "awaiting_approval"
    APPROVED = "approved"
    COMPLETED = "completed"
    REJECTED = "rejected"
    FAILED = "failed"
    DEAD_LETTER = "dead_letter"


class StepStatus(enum.StrEnum):
    """Outcome of one attempt of one typed workflow step."""

    SUCCEEDED = "succeeded"
    FAILED = "failed"
    TIMED_OUT = "timed_out"
    SKIPPED = "skipped"


class ProposalStatus(enum.StrEnum):
    """Human-review status of an allocation proposal."""

    PROPOSED = "proposed"
    APPROVED = "approved"
    REJECTED = "rejected"
