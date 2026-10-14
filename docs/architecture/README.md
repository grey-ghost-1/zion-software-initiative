# Architecture overview

Zion is a monorepo with a Next.js frontend and a modular FastAPI backend
backed by PostgreSQL. The current architecture is intentionally small:

```text
Browser -> Next.js web shell
                 |
                 +-> (not yet wired) typed HTTP boundary -> FastAPI modular monolith
                                                             |
                                                             +-> PostgreSQL (users, orgs,
                                                                 memberships, tokens, audits)
```

The frontend does not yet call the API at request time; the typed TS client in
`packages/api-client` exists and is tested, but pages read only build-time
static content (e.g. the evidence inventory) so this layer needs no running
backend to build. Shared packages (`packages/ui`, `packages/api-client`) are
introduced only when code is genuinely shared across `apps/web`.

## Principles

- Keep Harbor, Haven, and Beacon as explicit backend module boundaries when their
  first workflows arrive; this foundation adds no initiative-specific module.
- Keep transport, domain, and persistence concerns separable without distributing
  them into independent services prematurely.
- Keep the shared schema (users, organizations, memberships/roles, auth
  tokens, audit events) generic and reusable; initiative-specific fields
  belong to a later module, not this layer.
- Treat evidence, safety disclosures, accessibility, and data provenance as
  product behavior.
- Use environment-driven configuration without committing secrets.

See the [decision records](../decisions/) for the rationale behind current
boundaries, including [ADR 0005](../decisions/0005-shared-identity-rbac-and-audit-schema.md)
for the shared identity/RBAC/audit schema.
