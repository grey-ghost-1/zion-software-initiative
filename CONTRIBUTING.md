# Contributing to Zion

Thank you for helping build a careful, truthful public-interest software
portfolio.

## Before contributing

- Keep changes reviewable and scoped to an open issue or clearly explained goal.
- Use only synthetic examples or curated public data with a documented source.
- Do not add personal, patient, shelter-client, partner, credential, or secret data.
- Do not imply adoption, partnerships, clinical validation, field outcomes, or
  production readiness without evidence recorded in the evidence inventory.
- Preserve accessible semantics and keyboard operation.

## Development

Follow the setup in the root [README](README.md), then run:

```powershell
npm run check
```

Use focused commits and include tests for changed behavior. Python code is
formatted and linted by Ruff; TypeScript follows the Next.js ESLint configuration.

## Pull requests

Describe the user-facing and technical change, evidence and safety implications,
and the exact checks run. Link relevant decisions or issues. A pull request should
not activate deployment, ingest sensitive data, or introduce future dependencies
without an immediate use.

Security vulnerabilities must follow [SECURITY.md](SECURITY.md) instead of a
public issue.
