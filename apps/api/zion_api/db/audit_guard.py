"""Append-only enforcement for audit events, independent of database backend.

This complements the Postgres-only trigger created in the initial migration:
it works for every SQLAlchemy-supported backend (including SQLite, used in
tests), so audit immutability is verified without requiring a live Postgres
instance.
"""

from __future__ import annotations

from sqlalchemy import event
from sqlalchemy.orm import Session

from zion_api.models.audit_event import AuditEvent


class AuditEventImmutableError(RuntimeError):
    """Raised when code attempts to modify or delete an audit event."""


@event.listens_for(Session, "before_flush")
def _reject_audit_mutation(
    session: Session, flush_context: object, instances: object
) -> None:
    for obj in (*session.dirty, *session.deleted):
        if isinstance(obj, AuditEvent):
            raise AuditEventImmutableError(
                "Audit events are append-only and cannot be updated or deleted."
            )
