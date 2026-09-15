# ADR 0005: Add a shared identity, RBAC, and audit schema before any initiative

- **Status:** Accepted
- **Date:** 2026-09-15

## Context

GitHub issue #1 asks for the smallest professional-ready foundation that
Harbor, Haven, Beacon, or any other future initiative can share, without
building initiative-specific features yet. Every plausible initiative needs
accounts, organizations, roles, and an audit trail; building these once now
avoids each future initiative inventing its own.

## Decision

Add one shared, minimal schema to the modular monolith: synthetic `users`,
`organizations`, `memberships` (carrying a role), expiring session/auth
`tokens`, and append-only `audit_events`. Roles are limited to a small,
reusable set (`visitor`, `coordinator`, `navigator`, `volunteer`, `admin`)
chosen for likely future reuse, not because any initiative currently uses
them. Authentication is password + bcrypt + an expiring server-side session
token; authorization is server-side role checks plus organization-scoped
queries so a member of one organization cannot read or act on another
organization's data. Audit rows are guarded at the database level against
in-place update or delete. Exactly one admin-only endpoint exists, purely to
demonstrate the RBAC boundary works; it performs no product action. A
deterministic seed script creates synthetic demo accounts only, safe to
publish and safe to re-run.

Explicitly out of scope for this layer: registration, email delivery,
password reset, AI/agent execution, background queues, notifications,
analytics, and any Harbor/Haven/Beacon/Labs-specific feature or deployed
infrastructure.

## Consequences

Any future initiative starts with working accounts, organizations, roles, and
an audit trail instead of rebuilding them. The schema and role set must stay
generic; adding initiative-specific fields or roles later requires its own
decision record. Because roles are provisioned ahead of any real workflow,
reviewers should treat "reusable for later use" as a stated intent, not
evidence that visitor/coordinator/navigator/volunteer workflows exist today.
