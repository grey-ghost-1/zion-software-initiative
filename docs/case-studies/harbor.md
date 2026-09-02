# Harbor synthetic coordination vertical slice

## Need and intended stakeholders

Harbor explores how community coordinators could review assistance requests,
resource and shelter-like capacity, volunteer proposals, and fulfillment history
in one transparent workflow. Intended stakeholders for future discovery include
community coordinators, volunteers, service organizations, and people evaluating
safer coordination practices. None participated in or endorsed this prototype.

## What is implemented

The synthetic workflow creates a bounded request, returns deterministic matching
components and rejection reasons, records coordinator triage, proposes an
eligible volunteer plan, requires explicit approval to reserve capacity, records
synthetic fulfillment, and exposes a sanitized append-only audit timeline and
small metrics summary. Server-side roles and organization scope protect every
route.

The accessible Next.js route presents an Impact track and Engineering evidence
track alongside loading, empty, error, selection, approval, and completion
states. It uses the shared typed API client.

## Dignity, privacy, and safety

All records are fictional and clearly marked synthetic. The API excludes
personal/contact data, precise locations, confidential sites, medical/disability
details, immigration/benefit data, minors, protected traits, and unrestricted
text. Matching is advisory; a coordinator makes every state-changing choice.
Unknown or stale capacity is unavailable.

## Limitations

This is not a deployed service, emergency system, shelter booking service,
dispatch system, case-management tool, or evidence of aid delivery. There are no
real users, partners, outcomes, maps, notifications, model calls, or external
data feeds.

## Evidence

- API contracts: `apps/api/zion_api/routes/harbor.py`
- Deterministic rules and capacity transactions:
  `apps/api/zion_api/services/harbor.py`
- Database constraints: `apps/api/zion_api/models/harbor.py`
- Backend and concurrency tests: `apps/api/tests/test_harbor.py`
- Typed client: `packages/api-client/src/index.ts`
- Accessible workflow: `apps/web/src/app/harbor`

## Roadmap boundary

OpenFEMA data, maps, geocoding, notifications, and dispatch remain research
topics only. Any future work must begin with partner-led requirements and review
the [OCHA Data Responsibility
Guidelines](https://centre.humdata.org/data-responsibility/), [OpenFEMA terms and
conditions](https://www.fema.gov/about/openfema/terms-conditions), and [WCAG
2.2](https://www.w3.org/WAI/standards-guidelines/wcag/).
