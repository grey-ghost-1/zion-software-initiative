"""Audit-event writer used by routes that perform security-relevant actions."""

from __future__ import annotations

from sqlalchemy.orm import Session

from zion_api.models.audit_event import AuditEvent


def record_audit_event(
    db: Session,
    *,
    action: str,
    actor_user_id: str | None,
    organization_id: str | None = None,
    subject_type: str | None = None,
    subject_id: str | None = None,
    context: dict[str, object] | None = None,
) -> AuditEvent:
    """Insert one append-only audit event. Never updates or deletes."""

    event = AuditEvent(
        action=action,
        actor_user_id=actor_user_id,
        organization_id=organization_id,
        subject_type=subject_type,
        subject_id=subject_id,
        context=context or {},
    )
    db.add(event)
    db.flush()
    return event
