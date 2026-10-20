# Zion Software Initiative

Zion is an independent social-impact software initiative hub and a recruiter-facing
engineering portfolio for **Justin Wimmer**, an entry-level full-stack/backend
developer. The repository is not connected to the portfolio website project or its
branding.

## Current status

**Repository foundation only.** This first layer provides a runnable Next.js shell,
a minimal FastAPI service, shared visual tokens, tests, CI, and project governance.
There are no live product workflows, production deployments, users, partnerships,
or measured field outcomes.

The focused initiatives are:

- **Harbor** — a planned community-resource coordination platform, starting with a
  Roanoke, Virginia pilot for food banks, shelters, and veteran services.
- **GreenHub (Roanoke Green Hub)** — a planned effort to coordinate Roanoke-area
  environmental initiatives, such as cleanups, trail days, volunteer sign-ups, and
  an impact counter. It is intended as the first implementation of Harbor's
  community-coordination model.

Both initiatives are planned, not live products. No users, partners, or field
outcomes are claimed, and no demo is currently published.

## Safety and data boundaries

Zion currently uses only synthetic examples and curated public data. Do not add
personal, vulnerable-population, patient, shelter-client, or partner data. Nothing
in this repository provides medical advice, diagnosis, emergency response, or
production humanitarian capability. See the [security policy](SECURITY.md),
[threat model](docs/security/threat-model.md), and
[evidence inventory](docs/evidence/inventory.json).

## Repository map

| Path | Purpose |
| --- | --- |
| `apps/web` | Next.js App Router landing shell |
| `apps/api` | Modular FastAPI foundation and health contract |
| `packages/config` | Shared beach-palette design tokens |
| `packages/ui` | Reserved, documented boundary; no package yet |
| `packages/api-client` | Reserved, documented boundary; no package yet |
| `docs/architecture` | Architecture overview |
| `docs/decisions` | Architecture decision records |
| `docs/security` | Security boundaries and threat model |
| `docs/case-studies` | Reserved for evidence-backed case studies |
| `infra` | Deployment planning boundary; no active infrastructure |

## Prerequisites

- Node.js 22.x and npm 10.9.8
- Python 3.13

## Local development

From the repository root:

```powershell
npm ci
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --requirement apps\api\requirements-dev.lock
npm run dev:web
```

In a second PowerShell terminal, activate the same virtual environment and run:

```powershell
npm run dev:api
```

The web app is at `http://localhost:3000`. The API liveness endpoint is
`http://localhost:8000/health/live`; readiness intentionally returns HTTP 503
while Zion is foundation-only.

macOS/Linux activation uses `source .venv/bin/activate`. All npm commands below
are otherwise platform-independent.

## Developer commands

| Command | Result |
| --- | --- |
| `npm run dev:web` | Start the Next.js development server |
| `npm run dev:api` | Start FastAPI with reload |
| `npm run lint` | Lint TypeScript and Python |
| `npm run typecheck` | Type-check both apps |
| `npm test` | Test web, API, evidence, and claim boundaries |
| `npm run check:python` | Compile Python sources and tests |
| `npm run build` | Create the production web build |
| `npm run check` | Run the complete local CI-equivalent sequence |

## Planned deployment

The intended topology is Vercel for the frontend, Render for the API, and a
managed PostgreSQL service using SQLAlchemy and Alembic. None is provisioned or
activated in this layer. Architecture will begin as a modular monolith so domain
boundaries can evolve without premature distributed-system complexity.

## Contributing

Read [CONTRIBUTING.md](CONTRIBUTING.md) before opening a change. Security concerns
should follow [SECURITY.md](SECURITY.md), not a public issue.
