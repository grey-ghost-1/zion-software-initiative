# ADR 0001: Begin with a modular monolith

- **Status:** Accepted
- **Date:** 2026-09-01

## Context

Initiatives may develop different domain language, but the repository has
no product workflows, operating history, or scaling evidence.

## Decision

Build one FastAPI deployable with explicit Harbor and Haven module boundaries.
Keep modules independently testable and avoid cross-module persistence access.

## Consequences

Deployment and local development remain simple. Boundaries must be enforced in
code review, and a future service extraction requires measured operational need.
