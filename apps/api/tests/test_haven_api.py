"""Public Haven endpoint tests: curated cards, resource provenance and
freshness, deterministic routing, and validation gating."""

from __future__ import annotations

from collections.abc import Iterator
from datetime import date

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from zion_api.haven_seed import seed_haven_content
from zion_api.main import app
from zion_api.models.haven import (
    HavenConcernCategory,
    HavenGuidanceCard,
    HavenProvenance,
    HavenResource,
    HavenResourceKind,
    HavenSourceMode,
)
from zion_api.routes.haven import get_optional_db

OFFICIAL_DOMAINS = (
    "988lifeline.org",
    "findtreatment.gov",
    "findahealthcenter.hrsa.gov",
    "medlineplus.gov",
)


@pytest.fixture
def haven_client(db_session: Session, client: TestClient) -> Iterator[TestClient]:
    seed_haven_content(db_session)
    db_session.commit()

    def override() -> Iterator[Session | None]:
        yield db_session

    app.dependency_overrides[get_optional_db] = override
    try:
        yield client
    finally:
        app.dependency_overrides.pop(get_optional_db, None)


def test_guidance_cards_are_public_and_carry_citations(haven_client: TestClient) -> None:
    response = haven_client.get("/haven/guidance-cards")
    assert response.status_code == 200
    cards = response.json()["cards"]
    assert len(cards) >= 5
    for card in cards:
        assert card["original_text"]
        assert card["plain_text"]
        assert card["source_name"]
        assert card["source_url"].startswith("https://")
        assert card["jurisdiction"] == "US"
        assert card["reviewed_on"]


def test_invalid_card_is_never_served(
    haven_client: TestClient, db_session: Session
) -> None:
    db_session.add(
        HavenGuidanceCard(
            slug="broken-card",
            category=HavenConcernCategory.GENERAL_QUESTION,
            title="Broken card",
            original_text="Take 650 mg every 6 hours. Do not exceed 3000 mg.",
            plain_text="You have the flu; take as much as you like.",
            source_name="Synthetic test entry",
            source_url="https://example.org/broken",
            jurisdiction="US",
            reviewed_on=date(2026, 9, 1),
        )
    )
    db_session.commit()

    response = haven_client.get("/haven/guidance-cards")
    slugs = {card["slug"] for card in response.json()["cards"]}
    assert "broken-card" not in slugs


def test_resources_expose_full_provenance_and_official_urls(haven_client: TestClient) -> None:
    response = haven_client.get("/haven/resources")
    assert response.status_code == 200
    resources = response.json()["resources"]
    assert len(resources) >= 5

    live = [r for r in resources if r["source_mode"] == "live_official"]
    assert {r["slug"] for r in live} >= {
        "988-lifeline",
        "findtreatment-gov",
        "hrsa-find-a-health-center",
        "medlineplus",
    }
    for resource in resources:
        for field in (
            "url",
            "jurisdiction",
            "provenance",
            "source_mode",
            "reviewed_on",
            "retrieved_on",
            "review_valid_until",
            "freshness",
        ):
            assert resource[field], field
    for resource in live:
        assert any(domain in resource["url"] for domain in OFFICIAL_DOMAINS)

    synthetic = [r for r in resources if r["source_mode"] == "synthetic_demo"]
    assert synthetic, "the synthetic demo entry must be explicitly labeled"
    assert all(r["provenance"] == "synthetic" for r in synthetic)


def test_stale_resource_is_flagged_needs_review(
    haven_client: TestClient, db_session: Session
) -> None:
    db_session.add(
        HavenResource(
            slug="stale-resource",
            name="Stale synthetic resource",
            description="Synthetic entry whose review window has lapsed.",
            url="https://example.org/stale",
            kind=HavenResourceKind.HEALTH_EDUCATION,
            jurisdiction="US",
            provenance=HavenProvenance.SYNTHETIC,
            source_mode=HavenSourceMode.SYNTHETIC_DEMO,
            reviewed_on=date(2020, 1, 1),
            retrieved_on=date(2020, 1, 1),
            review_valid_until=date(2020, 6, 1),
            is_available=True,
        )
    )
    db_session.commit()

    response = haven_client.get("/haven/resources")
    by_slug = {r["slug"]: r for r in response.json()["resources"]}
    assert by_slug["stale-resource"]["freshness"] == "needs_review"
    assert by_slug["medlineplus"]["freshness"] == "current"


def test_unavailable_resource_is_excluded_everywhere(
    haven_client: TestClient, db_session: Session
) -> None:
    db_session.add(
        HavenResource(
            slug="unavailable-resource",
            name="Unavailable synthetic resource",
            description="Synthetic entry marked unavailable.",
            url="https://example.org/unavailable",
            kind=HavenResourceKind.HEALTH_EDUCATION,
            jurisdiction="US",
            provenance=HavenProvenance.SYNTHETIC,
            source_mode=HavenSourceMode.SYNTHETIC_DEMO,
            reviewed_on=date(2026, 9, 1),
            retrieved_on=date(2026, 9, 1),
            review_valid_until=date(2027, 3, 1),
            is_available=False,
        )
    )
    db_session.commit()

    listing = haven_client.get("/haven/resources").json()["resources"]
    assert "unavailable-resource" not in {r["slug"] for r in listing}

    navigation = haven_client.post(
        "/haven/navigations",
        json={
            "concern_category": "cough_or_cold",
            "duration": "one_to_three_days",
            "severity": "mild",
        },
    ).json()
    assert "unavailable-resource" not in {r["slug"] for r in navigation["resources"]}


@pytest.mark.parametrize(
    ("payload", "expected_outcome"),
    [
        (
            {"concern_category": "cough_or_cold", "duration": "one_to_three_days",
             "severity": "mild"},
            "self_care_education",
        ),
        (
            {"concern_category": "fever_or_flu", "duration": "over_one_week",
             "severity": "moderate"},
            "clinician_soon",
        ),
        (
            {"concern_category": "minor_injury", "duration": "under_one_day",
             "severity": "severe"},
            "clinician_soon",
        ),
        (
            {"concern_category": "low_mood", "duration": "over_one_week",
             "severity": "moderate"},
            "mental_health_support",
        ),
        (
            {"concern_category": "cost_or_coverage", "duration": "over_one_week",
             "severity": "mild"},
            "low_cost_care_routing",
        ),
    ],
)
def test_routing_is_deterministic_and_non_diagnostic(
    haven_client: TestClient, payload: dict, expected_outcome: str
) -> None:
    first = haven_client.post("/haven/navigations", json=payload)
    second = haven_client.post("/haven/navigations", json=payload)
    assert first.status_code == second.status_code == 200
    body = first.json()
    assert body == second.json()

    assert body["outcome"] == expected_outcome
    assert body["synthetic"] is True
    assert body["stored"] is False
    assert body["next_steps"]
    assert "not" in body["disclaimer"] and "diagnosis" in body["disclaimer"]
    assert body["emergency"]["active"] is False


def test_mental_health_routing_includes_crisis_and_treatment_resources(
    haven_client: TestClient,
) -> None:
    body = haven_client.post(
        "/haven/navigations",
        json={
            "concern_category": "stress_or_anxiety",
            "duration": "over_one_week",
            "severity": "moderate",
        },
    ).json()
    slugs = {r["slug"] for r in body["resources"]}
    assert "988-lifeline" in slugs
    assert "findtreatment-gov" in slugs
    cards = {card["slug"] for card in body["guidance_cards"]}
    assert "stress-basics" in cards


def test_navigation_output_contains_no_prohibited_content(haven_client: TestClient) -> None:
    from zion_api.services.haven_content import prohibited_content_violations

    body = haven_client.post(
        "/haven/navigations",
        json={
            "concern_category": "fever_or_flu",
            "duration": "one_to_three_days",
            "severity": "moderate",
        },
    ).json()
    texts = [body["disclaimer"], *body["next_steps"]]
    for card in body["guidance_cards"]:
        texts.append(card["plain_text"])
    for text in texts:
        assert prohibited_content_violations(text) == [], text


def test_overlong_concern_text_is_rejected_by_schema(haven_client: TestClient) -> None:
    response = haven_client.post(
        "/haven/navigations",
        json={
            "concern_category": "general_question",
            "duration": "under_one_day",
            "severity": "mild",
            "concern_text": "x" * 281,
        },
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"
