# Architecture overview

Zion is a monorepo with a Next.js frontend and a modular FastAPI backend
backed by PostgreSQL. The current architecture is intentionally small:

```text
Browser -> Next.js shell + Harbor route
                 |
                 +-> typed HTTP client -> FastAPI modular monolith
                                            |
                                            +-> PostgreSQL (foundation + Harbor)
```

The Harbor client component calls the API only after a user starts its synthetic
workflow. Other pages remain static, so the site can still build without a
running backend. The shared typed client mirrors every implemented endpoint.

## Principles

- Keep Harbor as an explicit route/service/model boundary; do not create Haven
  or Beacon modules until a separately reviewed slice exists.
- Keep transport, domain, and persistence concerns separable without distributing
  them into independent services prematurely.
- Keep the shared schema (users, organizations, memberships/roles, auth
  tokens, audit events) generic and reusable; initiative-specific fields
  remain separate from Harbor-specific tables.
- Treat evidence, safety disclosures, accessibility, and data provenance as
  product behavior.
- Use environment-driven configuration without committing secrets.

See the [decision records](../decisions/) for the rationale behind current
boundaries, including [ADR 0005](../decisions/0005-shared-identity-rbac-and-audit-schema.md)
for the shared identity/RBAC/audit schema.
Harbor's bounded workflow is documented in [ADR 0006](../decisions/0006-harbor-human-controlled-coordination.md).
