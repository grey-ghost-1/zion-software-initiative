# @zion/api-client

A small, fully typed TypeScript client for the endpoints implemented in this
foundation layer: `GET /health/live`, `GET /health/ready`, `POST /auth/login`,
`GET /me`, and `GET /admin/organizations/{slug}/members`. Types mirror the
FastAPI Pydantic response schemas exactly, and every non-2xx response is
surfaced as a typed `ZionApiError` (code, HTTP status, request id) — except
`getReadiness`, which always resolves so a caller can render a truthful
degraded state instead of catching an exception for an expected condition.

Extend this client only alongside a real, already-implemented API endpoint —
never speculatively ahead of the backend.

Run `npm run test --workspace=@zion/api-client` to run its unit tests.
