# Foundation threat model

## Scope

This model covers the public source repository, static Next.js landing shell,
minimal FastAPI health routes, dependency supply chain, and CI. There is no
deployed service, authentication, database, user submission, or AI execution in
scope.

## Assets and trust boundaries

- Source integrity, branch history, and GitHub workflow permissions.
- Maintainer and contributor credentials, which must remain outside the repository.
- Public readers' ability to distinguish implemented evidence from plans.
- The future boundary between a browser, Vercel frontend, Render API, managed
  PostgreSQL, and external data/model providers.

## Current threats and controls

| Threat | Current control |
| --- | --- |
| Secret or sensitive-data disclosure | Ignore rules, examples without values, contribution policy, public-data-only ADR |
| Dependency or CI compromise | Lock/pin strategy, read-only workflow token, Dependabot, bounded CI timeouts |
| Misleading capability or impact claims | Explicit status disclosures, evidence inventory, unsupported-claim test |
| Health endpoint information leakage | Minimal fixed liveness body; no version, host, dependency, or environment details |
| Accidental traffic routing to an incomplete service | Readiness returns HTTP 503 and `ready: false` |
| Accessibility exclusion | Semantic landmarks, skip link, focus styles, reduced-motion handling, component tests |

## Deferred threats

Before accepting user input, identity, database records, external model calls, or
deployment traffic, update this model for authorization, tenant isolation, abuse
prevention, prompt injection, model/data-provider retention, auditability,
incident response, backups, geographic data sensitivity, and vulnerable-user
safety.

## Non-goals

The foundation is not a clinical system, emergency service, case-management
system, autonomous decision maker, or production humanitarian platform.
