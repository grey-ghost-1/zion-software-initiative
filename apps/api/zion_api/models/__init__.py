"""ORM models for the shared Zion schema.

Importing this package registers every model (and the audit-immutability
guard) with the shared declarative base, which Alembic's env.py relies on for
autogeneration diffing.
"""

from __future__ import annotations

from zion_api.db import audit_guard as audit_guard  # noqa: F401  (registers event listener)
from zion_api.models.audit_event import AuditEvent
from zion_api.models.auth_token import AuthToken
from zion_api.models.beacon import (
    AllocationProposal,
    FixtureProvenance,
    WorkflowDefinition,
    WorkflowRun,
    WorkflowRunStep,
)
from zion_api.models.enums import ProposalStatus, Role, RunStatus, StepStatus
from zion_api.models.membership import Membership
from zion_api.models.organization import Organization
from zion_api.models.user import User

__all__ = [
    "AllocationProposal",
    "AuditEvent",
    "AuthToken",
    "FixtureProvenance",
    "Membership",
    "Organization",
    "ProposalStatus",
    "Role",
    "RunStatus",
    "StepStatus",
    "User",
    "WorkflowDefinition",
    "WorkflowRun",
    "WorkflowRunStep",
]
