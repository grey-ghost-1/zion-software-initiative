"""Beacon workflow models: definition, runs, step events, provenance, proposals.

Everything stored here is synthetic demonstration data. Step events and
fixture provenance rows are append-only by convention (the engine never
updates or deletes them); no raw fixture text or free-form prompt content is
ever persisted -- only structured flags, counters, and identifiers.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from zion_api.db.base import Base
from zion_api.models.enums import ProposalStatus, RunStatus, StepStatus


def _new_id() -> str:
    return str(uuid.uuid4())


def _enum_column(enum_cls: type, length: int = 30) -> Enum:
    return Enum(
        enum_cls,
        native_enum=False,
        validate_strings=True,
        length=length,
        values_callable=lambda cls: [member.value for member in cls],
    )


class WorkflowDefinition(Base):
    """One fixed, versioned workflow definition (seeded, never user-authored)."""

    __tablename__ = "beacon_workflow_definitions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_id)
    key: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    version: Mapped[str] = mapped_column(String(20), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    policy_version: Mapped[str] = mapped_column(String(50), nullable=False)
    # Ordered list of {"step_key": ..., "tool": ...}; tools must exist in the
    # code-level typed registry -- the engine rejects anything else.
    steps: Mapped[list[dict[str, object]]] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class FixtureProvenance(Base):
    """Provenance for one canned synthetic fixture used by a run."""

    __tablename__ = "beacon_fixture_provenance"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_id)
    run_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("beacon_workflow_runs.id", ondelete="CASCADE"), nullable=False
    )
    fixture_id: Mapped[str] = mapped_column(String(100), nullable=False)
    source_label: Mapped[str] = mapped_column(String(200), nullable=False)
    synthetic: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    license_note: Mapped[str] = mapped_column(String(300), nullable=False)
    checksum_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    effective_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    retrieved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    run: Mapped[WorkflowRun] = relationship(back_populates="provenance")


class WorkflowRun(Base):
    """One idempotent execution of the fixed Beacon demonstration workflow."""

    __tablename__ = "beacon_workflow_runs"
    __table_args__ = (
        UniqueConstraint(
            "organization_id", "idempotency_key", name="uq_beacon_run_org_idempotency"
        ),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_id)
    workflow_key: Mapped[str] = mapped_column(String(100), nullable=False)
    workflow_version: Mapped[str] = mapped_column(String(20), nullable=False)
    policy_version: Mapped[str] = mapped_column(String(50), nullable=False)
    organization_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    created_by_user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    idempotency_key: Mapped[str] = mapped_column(String(100), nullable=False)
    scenario: Mapped[str] = mapped_column(String(50), nullable=False)
    fixture_id: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[RunStatus] = mapped_column(_enum_column(RunStatus), nullable=False)
    # Structured, sanitized outcome data only: counters, flags, policy check
    # results -- never raw fixture text.
    policy_results: Mapped[list[dict[str, object]]] = mapped_column(
        JSON, nullable=False, default=list
    )
    metrics: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
    disclosures: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    replay_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    steps: Mapped[list[WorkflowRunStep]] = relationship(
        back_populates="run", order_by="WorkflowRunStep.seq"
    )
    provenance: Mapped[list[FixtureProvenance]] = relationship(back_populates="run")
    proposal: Mapped[AllocationProposal | None] = relationship(back_populates="run")


class WorkflowRunStep(Base):
    """Append-only record of one attempt of one typed step in a run."""

    __tablename__ = "beacon_workflow_run_steps"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_id)
    run_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("beacon_workflow_runs.id", ondelete="CASCADE"), nullable=False
    )
    seq: Mapped[int] = mapped_column(Integer, nullable=False)
    step_key: Mapped[str] = mapped_column(String(100), nullable=False)
    tool_name: Mapped[str] = mapped_column(String(100), nullable=False)
    attempt: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    status: Mapped[StepStatus] = mapped_column(_enum_column(StepStatus), nullable=False)
    # Sanitized structured detail only (flags, counters, ids) -- never raw text.
    detail: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    run: Mapped[WorkflowRun] = relationship(back_populates="steps")


class AllocationProposal(Base):
    """One explainable, human-reviewed synthetic supply allocation proposal."""

    __tablename__ = "beacon_allocation_proposals"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_id)
    run_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("beacon_workflow_runs.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    status: Mapped[ProposalStatus] = mapped_column(_enum_column(ProposalStatus), nullable=False)
    # [{"zone_id", "item", "quantity", "reason"}] -- deterministic heuristic output.
    lines: Mapped[list[dict[str, object]]] = mapped_column(JSON, nullable=False, default=list)
    # [{"zone_id", "item", "quantity", "reason"}] -- unmet or rejected demand.
    unmet_demand: Mapped[list[dict[str, object]]] = mapped_column(
        JSON, nullable=False, default=list
    )
    decided_by_user_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    decided_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    decision_note: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    run: Mapped[WorkflowRun] = relationship(back_populates="proposal")
