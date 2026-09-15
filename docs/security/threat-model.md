# Foundation threat model

## Scope

This model covers the public source repository, the accessible Next.js
dual-audience shell, the modular FastAPI service including authentication,
role-based access control, and organization isolation, the PostgreSQL-backed
shared schema plus Harbor's synthetic needs, resources, capacity, volunteer
availability, and plans, Haven's synthetic navigation plans and curated
guidance/resources, dependency supply chain, and CI. There is no deployed
service, real user registration, external data/model provider integration, or
AI execution in scope.

## Assets and trust boundaries

- Source integrity, branch history, and GitHub workflow permissions.
- Maintainer and contributor credentials, which must remain outside the repository.
- Synthetic demo account credentials and session tokens (bcrypt-hashed
  passwords, expiring server-side tokens); no real personal data exists to
  protect in this layer.
- Organization boundaries: one organization's memberships, tokens, and audit
  events must never be readable or actionable by a member of another
  organization.
- The append-only audit log as a record of login and admin-action events.
- Public readers' ability to distinguish implemented evidence from plans.
- The future boundary between a browser, Vercel frontend, Render API, managed
  PostgreSQL, and external data/model providers.

## Current threats and controls

| Threat | Current control |
| --- | --- |
| Secret or sensitive-data disclosure | Ignore rules, examples without values, contribution policy, public-data-only ADR, no plaintext passwords/tokens in logs |
| Dependency or CI compromise | Lock/pin strategy, read-only workflow token, Dependabot, bounded CI timeouts |
| Misleading capability or impact claims | Explicit status disclosures, evidence inventory, unsupported-claim test |
| Health endpoint information leakage | Minimal fixed liveness body; readiness reports only `status`/`ready`/`detail`, no version, host, dependency, or environment details |
| Password compromise via weak hashing | bcrypt password hashing; passwords never logged, returned, or stored in plaintext |
| Session token theft or replay after expiry | Server-side session tokens with an enforced expiry (`ZION_SESSION_TOKEN_TTL_MINUTES`); expired or invalid tokens are rejected and tested |
| Cross-organization data access | Server-side RBAC plus organization-scoped queries; a request scoped to another organization returns not-found rather than leaking existence |
| Privilege escalation to admin-only actions | Server-side role check on the single admin-only demonstration endpoint, independent of any client-supplied role claim |
| Audit log tampering (covering tracks) | Audit events are append-only; the database rejects `UPDATE`/`DELETE` on the audit table at the trigger level, not just in application code |
| Unauthorized cross-origin requests | Strict, explicit `ZION_CORS_ALLOWED_ORIGINS` allow-list; no wildcard origin |
| Malformed/attacker-supplied request bodies | Typed Pydantic request/response schemas reject unexpected shapes; typed error envelope avoids leaking stack traces |
| Untraceable errors in production logs | Every request/response carries a request ID surfaced in both the error envelope and `X-Request-ID` header |
| Accidental traffic routing to an unready service | Readiness checks real database connectivity and returns HTTP 503/`ready: false` when the database is unreachable |
| Accessibility exclusion | Semantic landmarks, skip link, focus styles, reduced-motion handling, component tests |
| Harmful or opaque matching | Fixed rules expose components, rejection reasons, and uncertainty; protected traits are absent; no automatic assignment |
| Stale/unknown capacity presented as available | Missing, stale, or unknown capacity is rejected by matching and approval |
| Concurrent overbooking | Approval uses an atomic conditional update and the table enforces reserved + fulfilled <= total |
| Volunteer overexposure | Volunteer endpoint filters by the authenticated synthetic volunteer and returns assignment-only fields |
| Script injection in resource text | Typed JSON plus React text rendering; tests use hostile synthetic resource text and verify no element injection |
| Unsafe health guidance | Haven is non-diagnostic, routes emergency/crisis indicators first, accepts controlled synthetic fields only, and links curated resources |

## Deferred threats

Before accepting real user registration, external identity providers, real
personal data, external model calls, background job queues, notifications, or
production deployment traffic, update this model for rate limiting/brute-force
protection on login, token refresh/rotation, multi-factor authentication,
prompt injection, model/data-provider retention, incident response, backups,
geographic data sensitivity, real capacity provenance/freshness, volunteer
safety, coercion/retaliation risk, and vulnerable-user safety.

## Non-goals

The foundation is not a clinical system, emergency service, case-management
system, autonomous decision maker, or production humanitarian platform. It
performs no diagnosis, aid provision, or autonomous action, and claims no
partners, real users, or production impact.
