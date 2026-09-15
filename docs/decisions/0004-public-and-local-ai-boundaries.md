# ADR 0004: Keep AI execution local or explicitly bounded

- **Status:** Accepted
- **Date:** 2026-09-01

## Context

Future initiatives may explore AI orchestration in sensitive social-impact
contexts. Public interfaces can invite prompt injection, data leakage, unsafe
automation, and misleading claims of autonomy.

## Decision

This layer exposes no AI model, agent, or automated decision endpoint. Future
experiments default to synthetic/local data and human-reviewed outputs. Any public
AI capability requires explicit input/output limits, provider data terms, abuse
controls, observability, evaluation evidence, and a new security review.

## Consequences

AI orchestration remains outside the implemented product. No user should infer
autonomous humanitarian, health, or safety-critical operation.
