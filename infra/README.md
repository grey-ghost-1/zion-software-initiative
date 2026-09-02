# Infrastructure boundary

`docker-compose.yml` runs a local-only PostgreSQL instance for development and
manual testing (`npm run db:up`). It provisions nothing beyond a developer's
own machine.

No deployment infrastructure is provisioned in this layer. The planned
topology is a Vercel frontend, Render API, and managed PostgreSQL, but
activation and provider-specific configuration belong in a later reviewed
change.
