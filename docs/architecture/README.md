# Architecture overview

Zion is a monorepo with a Next.js frontend and a modular FastAPI backend
backed by PostgreSQL. The current architecture is intentionally small:

```text
Browser -> Next.js shared shell + canonical Harbor/Haven routes
                 |
                 +-> typed HTTP client -> FastAPI modular monolith
                                            |
                                            +-> PostgreSQL (foundation + Harbor + Haven)
```

The Harbor and Haven client components call the API only after a user starts a
synthetic workflow. Other pages remain static, so the site can still build
without a running backend. The shared typed client mirrors every implemented
endpoint.

The public information architecture has four primary destinations: Mission,
Architecture, Flagships, and Zion Labs. Harbor and Haven live at
`/flagships/harbor` and `/flagships/haven`; legacy non-Beacon project routes
redirect one way to those canonical routes. Removed Beacon routes remain absent
and are not redirected.

## Principles

- Keep Harbor and Haven as explicit route/service/model boundaries.
- Keep transport, domain, and persistence concerns separable without distributing
  them into independent services prematurely.
- Keep the shared schema (users, organizations, memberships/roles, auth
  tokens, audit events) generic and reusable; initiative-specific fields
  remain separate from initiative-specific tables.
- Treat evidence, safety disclosures, accessibility, and data provenance as
  product behavior.
- Use environment-driven configuration without committing secrets.

## Production-readiness boundary

Repository CI plus liveness and database-backed readiness endpoints are
implemented and tested. Hosted deployment, managed production PostgreSQL,
public HTTPS verification, monitoring, and a rollback exercise remain pending
or unverified. The diagram describes repository architecture, not a deployed
topology.

See the [decision records](../decisions/) for the rationale behind current
boundaries, including [ADR 0005](../decisions/0005-shared-identity-rbac-and-audit-schema.md)
for the shared identity/RBAC/audit schema.
Harbor's bounded workflow is documented in [ADR 0006](../decisions/0006-harbor-human-controlled-coordination.md).
