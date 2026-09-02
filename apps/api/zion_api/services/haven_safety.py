"""Deterministic Haven emergency and crisis handling.

This module is intentionally free of database, network, and model
dependencies so that emergency and crisis guidance can never be blocked by a
failing dependency. It uses only explicit boolean inputs and a conservative,
reviewable phrase list over a short, bounded text input.

The guidance text is fixed U.S.-scope content: 911 for immediate physical
danger and the official 988 Suicide & Crisis Lifeline (call, text, or chat)
for crisis support. Nothing here monitors anyone, contacts anyone, or adapts
its answer — and the copy says so explicitly.
"""

from __future__ import annotations

import enum
import re
import unicodedata
from dataclasses import dataclass


class SafetyEscalation(enum.StrEnum):
    NONE = "none"
    EMERGENCY_911 = "emergency_911"
    CRISIS_988 = "crisis_988"


NO_MONITORING_NOTE = (
    "This demonstration does not monitor you, store what you typed, alert anyone, "
    "or contact any service on your behalf. You must reach out directly."
)

NON_DIAGNOSTIC_DISCLAIMER = (
    "Haven is a portfolio demonstration, not a medical service. It does not provide "
    "diagnosis, treatment, or medical advice. For medical questions, talk with a "
    "licensed clinician."
)

EMERGENCY_HEADLINE = "If anyone is in immediate physical danger, call 911 now."
EMERGENCY_STEPS = (
    "Call 911 (United States) right away, or go to the nearest emergency room.",
    "If it is safe, stay with the person until help arrives.",
    "If you also need emotional crisis support, call or text 988 to reach the "
    "988 Suicide & Crisis Lifeline.",
)

CRISIS_HEADLINE = (
    "If you may hurt yourself or someone else, contact the 988 Suicide & Crisis "
    "Lifeline now — call or text 988, or chat at 988lifeline.org."
)
CRISIS_STEPS = (
    "Call or text 988 (United States) to reach the 988 Suicide & Crisis Lifeline, "
    "free and confidential, 24/7.",
    "Chat online at https://988lifeline.org/chat/.",
    "If there is immediate physical danger, call 911.",
)

# Conservative deterministic phrase lists. Matching is intentionally broad and
# err-on-the-side-of-escalation: euphemisms and common misspellings are
# included, and a false positive only ever surfaces standard emergency
# guidance. Phrases are matched against normalized text (lowercase, accents
# stripped, punctuation removed, whitespace collapsed).
_CRISIS_PHRASES: tuple[str, ...] = (
    "suicide",
    "suicidal",
    "suicde",
    "sucide",
    "suiside",
    "kill myself",
    "kil myself",
    "killing myself",
    "end my life",
    "end it all",
    "ending it all",
    "take my own life",
    "dont want to be here anymore",
    "dont want to live",
    "no reason to live",
    "better off dead",
    "better off without me",
    "want to disappear forever",
    "unalive",
    "self harm",
    "self harming",
    "hurt myself",
    "hurting myself",
    "harm myself",
    "cut myself",
    "cutting myself",
    "kms",
    "hurt someone else",
    "hurt somebody else",
    "kill someone",
    "kill somebody",
    "hurting someone else",
)

_EMERGENCY_PHRASES: tuple[str, ...] = (
    "chest pain",
    "chest pressure",
    "cant breathe",
    "can not breathe",
    "trouble breathing",
    "not breathing",
    "stopped breathing",
    "turning blue",
    "unconscious",
    "unresponsive",
    "passed out and wont wake",
    "seizure",
    "seizing",
    "stroke",
    "face drooping",
    "heart attack",
    "severe bleeding",
    "bleeding wont stop",
    "bleeding a lot",
    "choking",
    "overdose",
    "overdosed",
    "took too many pills",
    "poisoned",
    "anaphylaxis",
    "throat closing",
    "gun",
    "knife",
    "weapon",
    "someone is hurting me",
    "being attacked",
)

_APOSTROPHES = ("'", "\u2019", "\u02bc", "`")
_WORD_BOUNDED = re.compile(r"[^a-z0-9 ]+")


def normalize_text(text: str) -> str:
    """Lowercase, drop apostrophes, strip accents/punctuation, collapse whitespace."""

    lowered = text.lower()
    for apostrophe in _APOSTROPHES:
        lowered = lowered.replace(apostrophe, "")
    decomposed = unicodedata.normalize("NFKD", lowered)
    ascii_text = decomposed.encode("ascii", "ignore").decode("ascii")
    cleaned = _WORD_BOUNDED.sub(" ", ascii_text)
    return " ".join(cleaned.split())


def _contains_phrase(normalized: str, phrases: tuple[str, ...]) -> bool:
    padded = f" {normalized} "
    return any(f" {phrase} " in padded for phrase in phrases)


@dataclass(frozen=True)
class SafetyAssessment:
    escalation: SafetyEscalation
    crisis_language_detected: bool


def assess_safety(
    *,
    immediate_danger: bool,
    self_harm_risk: bool,
    concern_text: str | None,
) -> SafetyAssessment:
    """Deterministically decide whether emergency or crisis guidance applies.

    Explicit inputs always win, then phrase checks. Physical-danger phrases
    escalate to 911 guidance; self-harm/violence phrases escalate to 988
    guidance. Any other content in ``concern_text`` (including instructions
    that attempt to suppress this behavior) is ignored: text can only ever
    *add* an escalation, never remove one.
    """

    normalized = normalize_text(concern_text) if concern_text else ""
    crisis_detected = bool(normalized) and _contains_phrase(normalized, _CRISIS_PHRASES)
    emergency_detected = bool(normalized) and _contains_phrase(normalized, _EMERGENCY_PHRASES)

    if immediate_danger or emergency_detected:
        return SafetyAssessment(
            escalation=SafetyEscalation.EMERGENCY_911,
            crisis_language_detected=crisis_detected,
        )
    if self_harm_risk or crisis_detected:
        return SafetyAssessment(
            escalation=SafetyEscalation.CRISIS_988,
            crisis_language_detected=crisis_detected,
        )
    return SafetyAssessment(escalation=SafetyEscalation.NONE, crisis_language_detected=False)


def guidance_for(escalation: SafetyEscalation) -> tuple[str, tuple[str, ...]]:
    """Return the fixed headline and steps for an escalation."""

    if escalation is SafetyEscalation.EMERGENCY_911:
        return EMERGENCY_HEADLINE, EMERGENCY_STEPS
    if escalation is SafetyEscalation.CRISIS_988:
        return CRISIS_HEADLINE, CRISIS_STEPS
    raise ValueError("No fixed guidance exists for a non-escalated assessment.")
