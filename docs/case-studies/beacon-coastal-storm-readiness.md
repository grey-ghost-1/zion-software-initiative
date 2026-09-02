# Beacon: coastal-storm readiness demonstration

**Status:** working demonstration. Synthetic fixture data only — exploratory, not
an official hazard product, and it issues no warnings.

## Impact story

When a synthetic storm advisory arrives, Beacon validates provenance and
freshness, evaluates a versioned policy, proposes an explainable allocation of
synthetic supplies across synthetic community zones, and stops for a human
coordinator to approve or reject. Unmet and deferred demand is always reported.

## Engineering story

One fixed workflow (`coastal-storm-readiness`) demonstrates five areas through a
single deterministic engine (`apps/api/zion_api/services/beacon`):

1. **Orchestration** — fixed state machine, typed allowlisted tool registry,
   bounded retries, explicit timeout/dead-letter states, idempotency keys,
   coordinator-only replay.
2. **Workflow automation** — synthetic trigger scenarios and append-only run,
   step-event, and audit records.
3. **Safety/governance** — six policy checks with a recorded policy version,
   prompt-injection and sensitive-data guards (fixture text is data, never
   instructions), and a hard scope guard: no autonomous purchasing, dispatch,
   beneficiary ranking, evacuation orders, or public warnings.
4. **Logistics** — greedy severity/population heuristic with inventory
   conservation and never-negative invariants; explicitly not an optimizer.
5. **GeoAI** — canned GeoJSON-like layer with CRS, geometry, impossible
   coordinate, antimeridian, and staleness validation, plus a tabular
   equivalent.

Verified by `apps/api/tests/test_beacon_*.py`,
`packages/api-client/src/beacon.test.ts`, and
`apps/web/src/app/initiatives/beacon/page.test.tsx`.

## Roadmap references (not implemented)

Future hardening would consult the NIST AI Risk Management Framework and NIST
AI 600-1, the OWASP Top 10 for LLM Applications, the public National Weather
Service API and its disclaimers, and OpenStreetMap data under the ODbL. None of
these are integrated today; no live adapters exist.
