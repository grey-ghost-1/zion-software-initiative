# ADR 0004: Keep AI execution local or explicitly bounded

> Update 2026-10-20: Beacon was dropped from the initiative focus; see
> [ADR 0005](0005-harbor-greenhub-focus.md). The original decision below is
> retained as historical context.

- **Status:** Accepted
- **Date:** 2026-09-01

## Context

Beacon may later explore AI orchestration in sensitive social-impact contexts.
Public interfaces can invite prompt injection, data leakage, unsafe automation,
and misleading claims of autonomy.

## Decision

This layer exposes no AI model, agent, or automated decision endpoint. Future
experiments default to synthetic/local data and human-reviewed outputs. Any public
AI capability requires explicit input/output limits, provider data terms, abuse
controls, observability, evaluation evidence, and a new security review.

## Consequences

Beacon remains a documented direction rather than a working AI service. No user
should infer autonomous humanitarian, health, or safety-critical operation.
