# Zion Software Initiative

Zion is a software platform rooted in peace, justice, and human goodwill. It
does not incorporate Batcomputer branding, source, project copy, or assets;
Zion Labs provides attribution and immutable external evidence links only.

## Current status

**One shared foundation and two implemented Zion flagships.** The canonical
site map is Mission, Architecture, Flagships, and Zion Labs. The repository
provides an accessible Next.js shell, a modular FastAPI service with
authentication and role-based access control, a PostgreSQL-backed schema (via
SQLAlchemy 2 + Alembic) for synthetic users, organizations, memberships, and
audit events, a typed TypeScript API client, and the Harbor and Haven synthetic
demonstrations. There is no hosted production deployment, managed production
PostgreSQL, public HTTPS verification, real-user or partner use, or measured
field outcome. See
[GitHub issue #1](https://github.com/grey-ghost-1/zion-software-initiative/issues/1)
for the foundation scope and [GitHub issue #5](https://github.com/grey-ghost-1/zion-software-initiative/issues/5)
for the archive evidence.

Harbor and Haven are the only implemented Zion flagship demonstrations.
Interoperability entries in Zion Labs are unimplemented learning concepts only.
The prior-work page is an attributed index of an immutable external evidence
snapshot; it does not copy or incorporate that project's branding, source,
project copy, or assets.

No demo is currently deployed. Harbor is software evidence, not an available
coordination product or evidence of impact.

## What's implemented

- **Frontend shell** (`apps/web`): the homepage, Mission, Architecture,
  Flagships, canonical Harbor and Haven pages, Zion Labs, its interoperability
  roadmap, and its prior-work inventory behind one accessible shared layout
  (skip link, semantic landmarks, current-page navigation, and global
  disclosure).
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
- **Harbor** (`apps/api/zion_api/routes/harbor.py`, `apps/web/src/app/flagships/harbor`):
  synthetic needs/resources, transparent deterministic matching, coordinator
  triage and override reasons, atomic capacity reservation, volunteer plan
  approval, fulfillment, an append-only audit timeline, and small metrics.
  Unknown or stale capacity is unavailable, and protected traits are absent
  from request and scoring contracts.
- **Haven** (`apps/api/zion_api/routes/haven.py`, `apps/web/src/app/flagships/haven`):
  non-diagnostic synthetic concern navigation with emergency and crisis bypass,
  curated resources, validated guidance cards, and org-scoped review/close
  actions.

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
| `apps/web` | Next.js App Router shell plus Harbor and Haven experiences |
| `apps/api` | Modular FastAPI service: foundation plus Harbor and Haven routes/services |
| `apps/api/migrations` | Alembic migrations for the shared schema |
| `packages/config` | Shared beach-palette design tokens |
| `packages/ui` | Reusable `StatusBadge` and `CaseStudyCard` primitives |
| `packages/api-client` | Typed TypeScript client for the implemented API endpoints |
| `docs/architecture` | Architecture overview |
| `docs/decisions` | Architecture decision records |
| `docs/security` | Security boundaries and threat model |
| `docs/case-studies` | Evidence-backed case studies |
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

CI and the API health/readiness contracts are implemented and tested. Hosted
deployment, managed production PostgreSQL, public HTTPS verification,
operational monitoring, and a rollback exercise remain pending or unverified.
`infra/` provides a local development database via Docker Compose only. The
modular monolith keeps domain boundaries clear without implying production
infrastructure.

## Contributing

Read [CONTRIBUTING.md](CONTRIBUTING.md) before opening a change. Security concerns
should follow [SECURITY.md](SECURITY.md), not a public issue.
