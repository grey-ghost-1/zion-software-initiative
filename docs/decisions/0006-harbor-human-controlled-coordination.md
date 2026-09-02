# ADR 0006: Human-controlled Harbor coordination

## Status

Accepted for the synthetic Harbor prototype.

## Context

Resource matching can create harm when unavailable capacity is presented as
current, protected traits influence priority, or software silently turns a
ranking into a real assignment. Harbor needs to demonstrate engineering
behavior without collecting vulnerable-person data or implying operational
readiness.

## Decision

- Accept only controlled enums, a patterned synthetic reference, coarse zones,
  and a bounded quantity. Do not accept names, contacts, exact locations,
  confidential sites, narratives, medical/disability details, immigration or
  benefit data, or information about minors.
- Calculate deterministic matches from category, controlled eligibility, coarse
  zone, open status, capacity freshness/availability, and accessibility status.
  Return every component, rejection reason, and uncertainty. Protected traits
  are absent from both input and scoring.
- Treat missing, stale, and unknown capacity as unavailable. Approval performs
  one conditional database update; a check constraint independently rejects
  overbooking.
- Require a coordinator/admin to triage, propose, approve, and fulfill. Proposal
  does not reserve capacity. Approval is the explicit reservation boundary.
- Limit volunteers to assignment-specific synthetic fields. Keep state-changing
  events in the shared append-only audit log.

## Consequences

The demonstration is explainable and race-safe on SQLite tests and PostgreSQL's
transactional update semantics. It deliberately cannot provide live capacity,
dispatch, notifications, mapping, geocoding, or autonomous decision-making.
Those capabilities require separate data-responsibility and partner review.
