"""Plain-language card validation tests: number/unit/negation invariance and
prohibited diagnosis/dose/percentage output."""

from __future__ import annotations

import pytest

from zion_api.haven_seed import CURATED_CARDS
from zion_api.services.haven_content import (
    card_violations,
    invariance_violations,
    prohibited_content_violations,
)


def test_every_curated_card_passes_full_validation() -> None:
    assert CURATED_CARDS, "curated card set must not be empty"
    for card in CURATED_CARDS:
        assert card_violations(card.original_text, card.plain_text) == [], card.slug


def test_dropping_a_number_fails_invariance() -> None:
    original = "Take 650 mg every 6 hours. Do not exceed 3000 mg in 24 hours."
    plain = "Take 650 mg every 6 hours. Do not take too much in a day."
    violations = invariance_violations(original, plain)
    assert any("missing" in violation for violation in violations)


def test_changing_a_number_fails_invariance() -> None:
    original = "Take 650 mg every 6 hours."
    plain = "Take 6500 mg every 6 hours."
    violations = invariance_violations(original, plain)
    assert violations


def test_changing_a_unit_fails_invariance() -> None:
    original = "Give 5 ml of the liquid."
    plain = "Give 5 mg of the liquid."
    assert invariance_violations(original, plain)


def test_dropping_negation_fails_invariance() -> None:
    original = "Do not give aspirin to children."
    plain = "Give aspirin to children."
    violations = invariance_violations(original, plain)
    assert any("negation" in violation for violation in violations)


def test_dropping_a_warning_marker_fails_invariance() -> None:
    original = "Call 911 for emergency warning signs."
    plain = "Get help if things feel serious."
    violations = invariance_violations(original, plain)
    assert violations


def test_timing_change_fails_invariance() -> None:
    original = "Take 1 tablet every 6 hours."
    plain = "Take 1 tablet every 8 hours."
    assert invariance_violations(original, plain)


@pytest.mark.parametrize(
    ("label", "text"),
    [
        ("diagnosis", "Based on this, you have strep throat."),
        ("diagnosis", "This matches a diagnosis of influenza."),
        ("risk_percentage", "There is a 40% chance this is serious."),
        ("risk_percentage", "You face a 12 percent risk of complications."),
        ("medication_change", "You should double your dose tonight."),
        ("medication_change", "Just stop taking the medication."),
        ("prognosis", "You will recover within a week."),
        ("prognosis", "This affects life expectancy."),
        ("inline_url_source", "According to https://made-up-source.example/study this works."),
    ],
)
def test_prohibited_output_is_detected(label: str, text: str) -> None:
    assert label in prohibited_content_violations(text)


def test_safe_plain_language_passes_prohibited_content_check() -> None:
    text = (
        "You can take acetaminophen 650 mg by mouth every 6 hours if a fever reaches "
        "100.4 F or higher. Do not take more than 3000 mg within 24 hours."
    )
    assert prohibited_content_violations(text) == []
