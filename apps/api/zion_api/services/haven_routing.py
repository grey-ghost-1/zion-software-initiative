"""Deterministic, table-driven Haven routing.

Routing is a fixed lookup over controlled enum inputs — no model, no
probability, no free-text interpretation. Emergency and crisis escalation is
decided *before* this table is consulted (see ``haven_safety``) and always
wins.
"""

from __future__ import annotations

from zion_api.models.haven import (
    HavenConcernCategory,
    HavenConcernDuration,
    HavenResourceKind,
    HavenRoutingOutcome,
    HavenSeverity,
)
from zion_api.services.haven_safety import SafetyEscalation

_MENTAL_HEALTH_CATEGORIES = frozenset(
    {
        HavenConcernCategory.STRESS_OR_ANXIETY,
        HavenConcernCategory.LOW_MOOD,
        HavenConcernCategory.SLEEP_TROUBLE,
    }
)

_LONG_DURATIONS = frozenset(
    {HavenConcernDuration.FOUR_TO_SEVEN_DAYS, HavenConcernDuration.OVER_ONE_WEEK}
)

# Fixed, reviewable next-step options per outcome. These are navigation
# options, never medical advice or diagnosis.
NEXT_STEPS: dict[HavenRoutingOutcome, tuple[str, ...]] = {
    HavenRoutingOutcome.EMERGENCY_NOW: (
        "Call 911 (United States) or go to the nearest emergency room now.",
    ),
    HavenRoutingOutcome.CRISIS_SUPPORT_NOW: (
        "Call or text 988, or chat at 988lifeline.org, to reach the 988 Suicide & Crisis "
        "Lifeline now.",
    ),
    HavenRoutingOutcome.CLINICIAN_SOON: (
        "Contact a clinician soon — for example a primary care office, urgent care clinic, "
        "or nurse advice line.",
        "If cost is a barrier, community health centers offer care on a sliding fee scale.",
        "Read the matching plain-language card below so you know which warning signs mean "
        "you should seek care right away.",
    ),
    HavenRoutingOutcome.MENTAL_HEALTH_SUPPORT: (
        "Consider talking with a mental-health professional; the treatment locator below "
        "lists licensed options.",
        "If things ever feel like too much, the 988 Lifeline is available any time by "
        "call, text, or chat.",
        "Trusted plain-language education about stress, mood, and sleep is linked below.",
    ),
    HavenRoutingOutcome.LOW_COST_CARE_ROUTING: (
        "Use the health-center finder below to locate care offered on a sliding fee scale "
        "near you.",
        "Community health centers serve people regardless of ability to pay or insurance "
        "status.",
    ),
    HavenRoutingOutcome.SELF_CARE_EDUCATION: (
        "Review the matching plain-language card below for trusted self-care basics.",
        "If symptoms last longer, get worse, or worry you, contact a clinician.",
    ),
}

# Which curated resource kinds support each outcome.
RESOURCE_KINDS: dict[HavenRoutingOutcome, tuple[HavenResourceKind, ...]] = {
    HavenRoutingOutcome.EMERGENCY_NOW: (HavenResourceKind.CRISIS_SUPPORT,),
    HavenRoutingOutcome.CRISIS_SUPPORT_NOW: (
        HavenResourceKind.CRISIS_SUPPORT,
        HavenResourceKind.TREATMENT_LOCATOR,
    ),
    HavenRoutingOutcome.CLINICIAN_SOON: (
        HavenResourceKind.LOW_COST_CARE,
        HavenResourceKind.HEALTH_EDUCATION,
    ),
    HavenRoutingOutcome.MENTAL_HEALTH_SUPPORT: (
        HavenResourceKind.CRISIS_SUPPORT,
        HavenResourceKind.TREATMENT_LOCATOR,
        HavenResourceKind.HEALTH_EDUCATION,
    ),
    HavenRoutingOutcome.LOW_COST_CARE_ROUTING: (
        HavenResourceKind.LOW_COST_CARE,
        HavenResourceKind.HEALTH_EDUCATION,
    ),
    HavenRoutingOutcome.SELF_CARE_EDUCATION: (HavenResourceKind.HEALTH_EDUCATION,),
}


def route_concern(
    *,
    escalation: SafetyEscalation,
    category: HavenConcernCategory,
    duration: HavenConcernDuration,
    severity: HavenSeverity,
) -> HavenRoutingOutcome:
    """Map controlled inputs to one deterministic, non-diagnostic outcome."""

    if escalation is SafetyEscalation.EMERGENCY_911:
        return HavenRoutingOutcome.EMERGENCY_NOW
    if escalation is SafetyEscalation.CRISIS_988:
        return HavenRoutingOutcome.CRISIS_SUPPORT_NOW

    if category in _MENTAL_HEALTH_CATEGORIES:
        return HavenRoutingOutcome.MENTAL_HEALTH_SUPPORT
    if category is HavenConcernCategory.COST_OR_COVERAGE:
        return HavenRoutingOutcome.LOW_COST_CARE_ROUTING

    if severity is HavenSeverity.SEVERE:
        return HavenRoutingOutcome.CLINICIAN_SOON
    if severity is HavenSeverity.MODERATE and duration in _LONG_DURATIONS:
        return HavenRoutingOutcome.CLINICIAN_SOON
    return HavenRoutingOutcome.SELF_CARE_EDUCATION
