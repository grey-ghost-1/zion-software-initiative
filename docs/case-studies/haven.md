# Haven non-diagnostic navigation vertical slice

## Module purpose

Haven demonstrates plain-language navigation from a synthetic concern to
bounded next steps and curated official resources. It is not a medical service.

## How it fits Zion

Haven applies Zion's shared typed client, organization isolation, RBAC, audit,
provenance, and deterministic safety behavior to a non-clinical navigation
workflow.

## Architecture summary

The canonical Next.js demonstration calls deterministic FastAPI routes through
the typed client. Fixed emergency and crisis routing bypasses optional storage;
content validation preserves source facts; organization-scoped review actions
use PostgreSQL-backed models and append-only audit records.

## Boundaries and limitations

Scenarios are synthetic and ephemeral. Haven has no real patients, medical
records, PHI, live integrations, clinical review, deployment, or measured
outcomes. It offers no diagnosis, treatment, medication, prognosis, risk
percentage, or medical advice and makes no HIPAA-compliance claim.

## Demo and evidence

- Canonical demonstration: `apps/web/src/app/flagships/haven/page.tsx`
- Interactive component: `apps/web/src/app/initiatives/haven/HavenDemo.tsx`
- Deterministic routes: `apps/api/zion_api/services/haven_routing.py`
- Safety behavior: `apps/api/zion_api/services/haven_safety.py`
- API and web tests: `apps/api/tests/test_haven_safety.py` and
  `apps/web/src/app/flagships/haven/page.test.tsx`

## Interview story

- **Problem:** unfamiliar care language and service categories can make next
  steps difficult to understand.
- **Constraints:** no patient data, diagnosis, treatment recommendation, or
  weakening of fixed emergency and crisis guidance.
- **Architecture:** ephemeral synthetic UI scenarios, deterministic routing,
  validated content, curated provenance, and scoped review/audit endpoints.
- **Safety:** emergency and crisis indicators surface fixed U.S. 911/988
  guidance before optional dependencies.
- **Outcome:** an inspectable, non-operational demonstration of explainable
  navigation and reviewer controls.
