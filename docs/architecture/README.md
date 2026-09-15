# Architecture overview

Zion is a monorepo with a Next.js frontend and a modular FastAPI backend. The
initial architecture is intentionally small:

```text
Browser -> Next.js web shell
                 |
                 +-> future typed HTTP boundary -> FastAPI modular monolith
                                                    |
                                                    +-> future PostgreSQL
```

No frontend-to-API feature call or database connection exists in this foundation
layer. Shared packages are introduced only when code is genuinely shared.

## Principles

- Keep Harbor, Haven, and Beacon as explicit backend module boundaries when their
  first workflows arrive.
- Keep transport, domain, and persistence concerns separable without distributing
  them into independent services prematurely.
- Treat evidence, safety disclosures, accessibility, and data provenance as
  product behavior.
- Use environment-driven configuration without committing secrets.

See the [decision records](../decisions/) for the rationale behind current
boundaries.
