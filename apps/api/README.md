# Zion API

This package is a deliberately small FastAPI foundation. It exposes:

- `GET /health/live` — HTTP 200 with a non-leaking process liveness response.
- `GET /health/ready` — HTTP 503 while no production dependencies or product
  modules are configured.

Run from the repository root with `npm run dev:api` after installing
`requirements-dev.lock` in an active virtual environment. Start the server through
the root command so implementation-identifying server headers remain disabled.
