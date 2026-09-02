"""Validation for Haven's curated plain-language guidance cards.

Two guarantees are enforced before any card is served:

1. **Invariance** — the plain-language rewrite of a curated instruction must
   preserve every number, its attached unit, and every negation marker from
   the original text. A rewrite that drops "not", changes "3000 mg", or loses
   "every 6 hours" is rejected.
2. **Prohibited content** — no card (and no other Haven output text) may
   contain a diagnosis, a risk percentage, a treatment or medication change,
   a prognosis, or an invented inline source. Citations live only in the
   structured ``source_name``/``source_url`` fields.

All checks are deterministic string analysis; no model is involved.
"""

from __future__ import annotations

import re
from collections import Counter

from zion_api.services.haven_safety import normalize_text

_NUMBER_WITH_UNIT = re.compile(
    r"(\d+(?:\.\d+)?)\s*"
    r"(mg|mcg|g|kg|ml|l|f|c|hours|hour|hrs|hr|minutes|minute|mins|min|days|day|"
    r"weeks|week|tablets|tablet|capsules|capsule|doses|dose|tsp|tbsp|oz|ounces|percent|%)?\b"
)

_NEGATION_MARKERS = ("not", "no", "never", "avoid", "without", "dont", "cannot", "shouldnt")

_WARNING_MARKERS = ("911", "988", "emergency", "warning")

_PROHIBITED_PATTERNS: dict[str, re.Pattern[str]] = {
    "diagnosis": re.compile(
        r"\bdiagnos\w*\b|\byou (?:probably |likely |definitely )?have [a-z]", re.IGNORECASE
    ),
    "risk_percentage": re.compile(
        r"\d+(?:\.\d+)?\s*(?:%|percent)\s*(?:risk|chance|likelihood|probability)", re.IGNORECASE
    ),
    "medication_change": re.compile(
        r"\b(?:increase|decrease|double|halve|skip|stop|start)\b[^.]{0,60}"
        r"\b(?:dose|dosage|medication|prescription)\b",
        re.IGNORECASE,
    ),
    "prognosis": re.compile(
        r"\byou will (?:recover|die|get worse|be fine|be cured)\b|\blife expectancy\b",
        re.IGNORECASE,
    ),
    "inline_url_source": re.compile(r"https?://", re.IGNORECASE),
}


def _number_unit_pairs(text: str) -> Counter[tuple[str, str]]:
    normalized = normalize_text(text)
    pairs: Counter[tuple[str, str]] = Counter()
    for match in _NUMBER_WITH_UNIT.finditer(normalized):
        number, unit = match.group(1), match.group(2) or ""
        pairs[(number, unit)] += 1
    return pairs


def _negation_counts(text: str) -> Counter[str]:
    tokens = normalize_text(text).split()
    return Counter(token for token in tokens if token in _NEGATION_MARKERS)


def invariance_violations(original_text: str, plain_text: str) -> list[str]:
    """Explain every way ``plain_text`` fails to preserve safety-critical facts."""

    violations: list[str] = []

    original_numbers = _number_unit_pairs(original_text)
    plain_numbers = _number_unit_pairs(plain_text)
    if original_numbers != plain_numbers:
        missing = original_numbers - plain_numbers
        added = plain_numbers - original_numbers
        if missing:
            violations.append(f"numbers/units missing from plain text: {sorted(missing)}")
        if added:
            violations.append(f"numbers/units invented in plain text: {sorted(added)}")

    original_negations = _negation_counts(original_text)
    plain_negations = _negation_counts(plain_text)
    if original_negations != plain_negations:
        violations.append(
            "negation markers changed: "
            f"original={dict(original_negations)} plain={dict(plain_negations)}"
        )

    normalized_original = normalize_text(original_text)
    normalized_plain = normalize_text(plain_text)
    for marker in _WARNING_MARKERS:
        if marker in normalized_original and marker not in normalized_plain:
            violations.append(f"warning marker dropped from plain text: {marker!r}")

    return violations


_NEGATED_DIAGNOSIS_MENTION = re.compile(
    r"\b(?:no|not|never|cannot|doesn'?t|don'?t)\b[^.]{0,40}?\bdiagnos\w*\b", re.IGNORECASE
)


def prohibited_content_violations(text: str) -> list[str]:
    """Explain every prohibited-content match found in an output text.

    Negated mentions such as "does not provide diagnosis" are disclaimers, not
    diagnoses, and are masked before scanning; affirmative diagnosis language
    is still rejected.
    """

    scannable = _NEGATED_DIAGNOSIS_MENTION.sub(" ", text)
    return [label for label, pattern in _PROHIBITED_PATTERNS.items() if pattern.search(scannable)]


def card_violations(original_text: str, plain_text: str) -> list[str]:
    """All violations preventing a curated card from being served."""

    return invariance_violations(original_text, plain_text) + [
        f"prohibited content in plain text: {label}"
        for label in prohibited_content_violations(plain_text)
    ]
