# Security policy

## Supported versions

Zion is currently a foundation-stage repository with no deployed release.
Security fixes apply to the latest commit on `main`.

## Reporting a vulnerability

Do not open a public issue for a vulnerability or include exploit details in a
pull request. Use **Report a vulnerability** on this repository's Security tab to
open a private GitHub security advisory. If private reporting is unavailable,
contact the maintainer through the methods on
[the repository owner's profile](https://github.com/grey-ghost-1) before sharing
details.

Include the affected path, reproduction steps, impact, and any suggested
mitigation. Do not access data that is not yours, disrupt services, or use social
engineering while researching.

## Current boundary

There are no production services, accounts, databases, or accepted sensitive
datasets in this layer. Credentials, personal data, vulnerable-population data,
and real health data must never be committed. See the
[threat model](docs/security/threat-model.md) for the current security posture.
