# Zion Software Initiative

Zion is an independent social-impact software initiative hub and a recruiter-facing
engineering portfolio for **Justin Wimmer**, an entry-level full-stack/backend
developer. The repository is not connected to the Batcomputer project or its
branding.

## Current status

**Shared foundation, stage one, plus the first prototype slices.** This layer
provides an accessible Next.js shell, a modular FastAPI service with
authentication and role-based access control, a PostgreSQL-backed schema (via
SQLAlchemy 2 + Alembic) for synthetic users, organizations, memberships, and
audit events, a typed TypeScript API client, the static Zion Labs prior-work
archive, the Harbor synthetic coordination workflow, and the Beacon synthetic
coastal-storm readiness workflow demo. There are no live product workflows,
production deployments, real users, partnerships, or measured field outcomes.
See
[GitHub issue #1](https://github.com/grey-ghost-1/zion-software-initiative/issues/1)
for the foundation scope and [GitHub issue #5](https://github.com/grey-ghost-1/zion-software-initiative/issues/5)
for the archive evidence.

Harbor and Beacon are the implemented initiative prototypes. These directions
remain unimplemented:

- **Haven** — exploration of non-diagnostic health navigation.
- **Beacon** — synthetic coastal-storm readiness workflow automation.

No demo is currently deployed. Harbor is software evidence, not an available
coordination product or evidence of impact.

## What's implemented

- **Frontend shell** (`apps/web`): Home, Initiatives, Projects, Labs, Evidence, and
  About Justin pages behind one accessible shared layout (skip link, semantic
  landmarks, current-page navigation) using a shared beach-palette token set.
- **Prior-work archive** (`apps/web/src/app/labs`): a static Zion Labs page
  backed by checked-in JSON from the Batcomputer Portfolio snapshot, featuring
  four flagships and nineteen grouped secondary labs with no runtime GitHub
  calls and no asset reuse.
- **Reusable UI primitives** (`packages/ui`): a truthful `StatusBadge`
  (`implemented` / `in-development` / `planned`) and a `CaseStudyCard` for
  impact and engineering case studies.
- **API** (`apps/api`): modular FastAPI configuration, typed error envelopes
  with request IDs, safe logging (no secrets/PII), strict CORS, liveness and
  readiness probes backed by a real database check, and OpenAPI docs.
- **Database** (`apps/api/zion_api/models`, `apps/api/migrations`): SQLAlchemy 2
  models and an Alembic migration for synthetic users, organizations,
  memberships with roles, expiring session tokens, and append-only audit
  events (DB-enforced immutability).
- **Auth and RBAC**: bcrypt password hashing, `/auth/login`, `/me`,
  server-side role checks, and organization isolation (cross-organization
  reads return not-found, never leak existence). One admin-only demonstration
  endpoint. Login and admin actions each write an audit event.
- **Deterministic demo seed** (`apps/api/zion_api/seed.py`): synthetic demo
  accounts and organizations only, safe to run repeatedly against an empty
  database.
- **Typed TS client** (`packages/api-client`): covers every implemented
  endpoint above with types mirrored from the API schemas.
- **Labs archive** (`apps/web/src/app/labs`): a static Zion Labs page backed by
  checked-in JSON from the Batcomputer Portfolio snapshot, featuring four
  flagships and nineteen grouped secondary labs with no runtime GitHub calls.
- **Harbor** (`apps/api/zion_api/routes/harbor.py`, `apps/web/src/app/harbor`):
  synthetic needs/resources, transparent deterministic matching, coordinator
  triage and override reasons, atomic capacity reservation, volunteer plan
  approval, fulfillment, an append-only audit timeline, and small metrics.
- **Beacon** (`apps/api/zion_api/services/beacon`, `apps/web/src/app/initiatives/beacon`):
  one fixed synthetic workflow with typed tools, idempotent runs, policy and
  provenance checks, explainable allocation, and coordinator approval.
  Unknown/stale capacity is unavailable, and protected traits are absent from
  request and scoring contracts.

## Safety and data boundaries

Zion currently uses only synthetic examples and curated public data. Demo
accounts, organizations, and audit entries are synthetic and reset by the seed
script — never real personal, health, vulnerable-population, or location data.
Do not add personal, patient, shelter-client, or partner data. Nothing in this
repository provides medical advice, diagnosis, emergency response, or
production humanitarian capability, and it makes no claim of partners, real
users, production impact, or autonomous operation. See the
[security policy](SECURITY.md), [threat model](docs/security/threat-model.md),
and [evidence inventory](docs/evidence/inventory.json).

## Repository map

| Path | Purpose |
| --- | --- |
| `apps/web` | Next.js App Router dual-audience shell and Harbor workflow |
| `apps/api` | Modular FastAPI service: foundation plus Harbor routes/services |
| `apps/api/migrations` | Alembic migrations for the shared schema |
| `packages/config` | Shared beach-palette design tokens |
| `packages/ui` | Reusable `StatusBadge` and `CaseStudyCard` primitives |
| `packages/api-client` | Typed TypeScript client for the implemented API endpoints |
| `docs/architecture` | Architecture overview |
| `docs/decisions` | Architecture decision records |
| `docs/security` | Security boundaries and threat model |
| `docs/case-studies` | Evidence-backed case studies, including Harbor |
| `infra` | Docker Compose for local PostgreSQL only; no deployment infrastructure provisioned |

## Prerequisites

- Node.js 22.x and npm 10.9.8
- Python 3.13
- Docker Desktop (or another Docker Engine) for the local PostgreSQL container

## Local development

From the repository root:

```powershell
npm ci
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --requirement apps\api\requirements-dev.lock
npm run db:up
npm run db:migrate
npm run db:seed
npm run dev:web
```

In a second PowerShell terminal, activate the same virtual environment and run:

```powershell
npm run dev:api
```

The web app is at `http://localhost:3000`. The API liveness endpoint is
`http://localhost:8000/health/live`; readiness at
`http://localhost:8000/health/ready` checks real database connectivity and
returns HTTP 200/`ready: true` once PostgreSQL is up and migrated, or HTTP
503/`ready: false` otherwise. Interactive API docs are at
`http://localhost:8000/docs`. Copy `apps/api/.env.example` to `apps/api/.env`
and adjust values as needed; the deterministic seed accounts are documented in
`apps/api/zion_api/seed.py`.

macOS/Linux activation uses `source .venv/bin/activate`. All npm commands below
are otherwise platform-independent.

## Developer commands

| Command | Result |
| --- | --- |
| `npm run dev:web` | Start the Next.js development server |
| `npm run dev:api` | Start FastAPI with reload |
| `npm run db:up` / `npm run db:down` | Start/stop the local PostgreSQL container |
| `npm run db:migrate` | Apply Alembic migrations to the local database |
| `npm run db:seed` | Load the deterministic synthetic demo accounts |
| `npm run lint` | Lint TypeScript and Python |
| `npm run typecheck` | Type-check the web app and all TypeScript packages |
| `npm test` | Test web, packages, API, evidence, and claim boundaries |
| `npm run check:python` | Compile Python sources and tests |
| `npm run build` | Create the production web build |
| `npm run check` | Run the complete local CI-equivalent sequence |

## Planned deployment

The intended topology is Vercel for the frontend, Render for the API, and a
managed PostgreSQL service using the SQLAlchemy/Alembic schema already in this
repository. None is provisioned or activated in this layer — `infra/` only
provides a local development database via Docker Compose. Architecture began
as a modular monolith so domain boundaries can evolve without premature
distributed-system complexity.

## Contributing

Read [CONTRIBUTING.md](CONTRIBUTING.md) before opening a change. Security concerns
should follow [SECURITY.md](SECURITY.md), not a public issue.
