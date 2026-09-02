# Zion API

This package contains the FastAPI foundation and the synthetic Harbor vertical
slice. It exposes:

- `GET /health/live` — HTTP 200 with a non-leaking process liveness response.
- `GET /health/ready` — database-backed readiness without dependency details.
- `/auth`, `/me`, and `/admin` — synthetic account, membership, and RBAC
  demonstrations.
- `/harbor/{org_slug}` — bounded synthetic needs/resources, explainable
  matching, human triage, volunteer plan approval, transactional capacity,
  fulfillment, audit, and metrics.

Harbor accepts controlled synthetic fields only. Its matching returns rule
components, rejection reasons, and uncertainty; explicit approval is the atomic
capacity-reservation boundary. No live data, dispatch, notification, map,
model, or autonomous decision integration exists.

Run from the repository root with `npm run dev:api` after installing
`requirements-dev.lock` in an active virtual environment. Start the server through
the root command so implementation-identifying server headers remain disabled.
