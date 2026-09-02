# @zion/api-client

A small, fully typed TypeScript client for every implemented foundation and
Harbor endpoint. Harbor contracts cover synthetic needs/resources, transparent
matches, triage, plan proposal/approval/fulfillment, volunteer assignments,
audit, and metrics. Types mirror the FastAPI Pydantic response schemas, and
every non-2xx response is surfaced as a typed `ZionApiError` (code, HTTP status,
request id) — except `getReadiness`, which always resolves so a caller can
render a truthful degraded state instead of catching an expected exception.

Extend this client only alongside a real, already-implemented API endpoint —
never speculatively ahead of the backend.

Run `npm run test --workspace=@zion/api-client` to run its unit tests.
