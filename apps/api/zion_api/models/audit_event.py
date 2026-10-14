"""Append-only audit event model.

Audit events record that a security-relevant action happened (login, admin
action) without capturing sensitive free text. ``context`` must only ever
hold small, non-sensitive, structured values (counts, IDs, flags) -- never
health, vulnerability, or location data.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import JSON, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from zion_api.db.base import Base


class AuditEvent(Base):
    """One immutable record of a security-relevant action."""

    __tablename__ = "audit_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    action: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    actor_user_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    organization_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    subject_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    subject_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    context: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
