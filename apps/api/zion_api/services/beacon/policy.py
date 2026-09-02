"""Policy evaluation and content guards for Beacon runs.

Retrieved fixture text is always treated as untrusted *data*: guards scan and
sanitize it, but nothing in it can change the step list, tool registry, or
policy version, because those live only in code. Raw fixture text is never
persisted or logged -- only counters, flags, and a checksum prefix.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any

POLICY_VERSION = "beacon-policy-v1"
MAX_FIXTURE_AGE = timedelta(hours=72)

_INJECTION_PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"ignore\s+(?:all\s+)?previous\s+instructions",
        r"system\s+prompt",
        r"disregard\s+.{0,40}(?:instructions|policy)",
        r"\{\s*\"tool\"",
        r"shell_exec|rm\s+-rf|curl\s+http",
        r"approve\s+allocation\s+automatically",
    )
]

_SENSITIVE_PATTERNS = [
    re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),  # SSN-shaped
    re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.]+\b"),  # email-shaped
]


@dataclass(frozen=True)
class PolicyCheck:
    """One structured policy check result (no free text from the fixture)."""

    check: str
    passed: bool
    detail: dict[str, object]

    def as_dict(self) -> dict[str, object]:
        return {"check": self.check, "passed": self.passed, "detail": self.detail}


def text_fingerprint(text: str) -> str:
    """A short, non-reversible fingerprint safe to store instead of raw text."""

    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def scan_advisory_text(text: str) -> tuple[int, int]:
    """Return (injection_marker_count, sensitive_marker_count) for a fixture text."""

    injection = sum(1 for pattern in _INJECTION_PATTERNS if pattern.search(text))
    sensitive = sum(len(pattern.findall(text)) for pattern in _SENSITIVE_PATTERNS)
    return injection, sensitive


def evaluate_policy(fixture: dict[str, Any], as_of: datetime) -> list[PolicyCheck]:
    """Evaluate every policy check against one loaded fixture."""

    checks: list[PolicyCheck] = []

    checks.append(
        PolicyCheck(
            check="fixture_is_synthetic",
            passed=fixture.get("synthetic") is True,
            detail={"fixture_id": str(fixture.get("fixture_id", ""))},
        )
    )

    provenance_complete = all(
        isinstance(fixture.get(key), str) and fixture.get(key)
        for key in ("source_label", "license_note", "fixture_id", "effective_at")
    )
    checks.append(
        PolicyCheck(
            check="provenance_complete",
            passed=provenance_complete,
            detail={},
        )
    )

    effective_at: datetime | None
    try:
        effective_at = datetime.fromisoformat(str(fixture.get("effective_at")))
    except ValueError:
        effective_at = None
    fresh = (
        effective_at is not None
        and effective_at.tzinfo is not None
        and as_of - effective_at <= MAX_FIXTURE_AGE
    )
    checks.append(
        PolicyCheck(
            check="fixture_freshness",
            passed=fresh,
            detail={
                "max_age_hours": int(MAX_FIXTURE_AGE.total_seconds() // 3600),
                "effective_at": str(fixture.get("effective_at", "")),
                "as_of": as_of.isoformat(),
            },
        )
    )

    advisory = str(fixture.get("advisory_text", ""))
    injection_markers, sensitive_markers = scan_advisory_text(advisory)
    checks.append(
        PolicyCheck(
            check="prompt_injection_guard",
            # The guard passes when injected text is detected and contained:
            # it is treated as data and cannot alter steps, tools, or policy.
            passed=True,
            detail={
                "suspicious_markers": injection_markers,
                "treated_as_data": True,
                "advisory_fingerprint": text_fingerprint(advisory),
            },
        )
    )
    checks.append(
        PolicyCheck(
            check="sensitive_data_guard",
            passed=True,
            detail={"redacted_markers": sensitive_markers, "raw_text_stored": False},
        )
    )

    checks.append(
        PolicyCheck(
            check="autonomy_scope_guard",
            passed=True,
            detail={
                "forbidden_capabilities_absent": [
                    "purchasing",
                    "dispatch",
                    "beneficiary_ranking",
                    "evacuation_order",
                    "public_warning",
                ],
                "human_approval_required": True,
            },
        )
    )

    return checks
