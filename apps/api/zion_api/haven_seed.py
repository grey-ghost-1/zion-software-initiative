"""Deterministic Haven curated content seed.

Seeds the curated plain-language guidance cards and outbound resource
references. Idempotent: stable name-derived UUIDs and upsert-by-slug mean
repeated runs never duplicate or reshuffle content.

Every guidance card is validated against Haven's invariance and
prohibited-content rules at seed time, so invalid curated content can never
even enter the database.

Usage (after ``alembic upgrade head``):

    python -m zion_api.haven_seed
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import date

from sqlalchemy.orm import Session

from zion_api.db.session import get_engine
from zion_api.models.haven import (
    HavenConcernCategory,
    HavenGuidanceCard,
    HavenProvenance,
    HavenResource,
    HavenResourceKind,
    HavenSourceMode,
)
from zion_api.services.haven_content import card_violations

_NAMESPACE = uuid.UUID("6d3fbc0a-1a68-4f24-9d1e-c4b1d1f2ab77")

_REVIEWED_ON = date(2026, 9, 1)
_RETRIEVED_ON = date(2026, 9, 1)
_REVIEW_VALID_UNTIL = date(2027, 3, 1)


def _stable_id(*parts: str) -> str:
    return str(uuid.uuid5(_NAMESPACE, ":".join(parts)))


@dataclass(frozen=True)
class CuratedResource:
    slug: str
    name: str
    description: str
    url: str
    kind: HavenResourceKind
    provenance: HavenProvenance
    source_mode: HavenSourceMode


@dataclass(frozen=True)
class CuratedCard:
    slug: str
    category: HavenConcernCategory
    title: str
    original_text: str
    plain_text: str
    source_name: str
    source_url: str


CURATED_RESOURCES: tuple[CuratedResource, ...] = (
    CuratedResource(
        slug="988-lifeline",
        name="988 Suicide & Crisis Lifeline",
        description=(
            "Free, confidential crisis support in the United States, 24/7: call or "
            "text 988, or chat online. Administered by Vibrant Emotional Health with "
            "funding from SAMHSA (HHS)."
        ),
        url="https://988lifeline.org/",
        kind=HavenResourceKind.CRISIS_SUPPORT,
        provenance=HavenProvenance.NONPROFIT_OFFICIAL,
        source_mode=HavenSourceMode.LIVE_OFFICIAL,
    ),
    CuratedResource(
        slug="findtreatment-gov",
        name="FindTreatment.gov",
        description=(
            "SAMHSA's confidential locator for licensed mental-health and "
            "substance-use treatment providers in the United States."
        ),
        url="https://findtreatment.gov/",
        kind=HavenResourceKind.TREATMENT_LOCATOR,
        provenance=HavenProvenance.FEDERAL_AGENCY,
        source_mode=HavenSourceMode.LIVE_OFFICIAL,
    ),
    CuratedResource(
        slug="hrsa-find-a-health-center",
        name="HRSA Find a Health Center",
        description=(
            "HRSA's official locator for federally funded health centers that "
            "provide care on a sliding fee scale, regardless of insurance status."
        ),
        url="https://findahealthcenter.hrsa.gov/",
        kind=HavenResourceKind.LOW_COST_CARE,
        provenance=HavenProvenance.FEDERAL_AGENCY,
        source_mode=HavenSourceMode.LIVE_OFFICIAL,
    ),
    CuratedResource(
        slug="medlineplus",
        name="MedlinePlus",
        description=(
            "Plain-language health education from the National Library of Medicine "
            "(NIH), covering conditions, wellness, and medication basics."
        ),
        url="https://medlineplus.gov/",
        kind=HavenResourceKind.HEALTH_EDUCATION,
        provenance=HavenProvenance.FEDERAL_AGENCY,
        source_mode=HavenSourceMode.LIVE_OFFICIAL,
    ),
    CuratedResource(
        slug="demo-community-clinic",
        name="Demo Community Clinic (synthetic example)",
        description=(
            "A synthetic example clinic listing used to demonstrate how curated "
            "local directories would appear. Not a real clinic."
        ),
        url="https://example.org/zion-demo-clinic",
        kind=HavenResourceKind.LOW_COST_CARE,
        provenance=HavenProvenance.SYNTHETIC,
        source_mode=HavenSourceMode.SYNTHETIC_DEMO,
    ),
)


CURATED_CARDS: tuple[CuratedCard, ...] = (
    CuratedCard(
        slug="fever-medicine-instructions",
        category=HavenConcernCategory.FEVER_OR_FLU,
        title="Understanding fever medicine label instructions",
        original_text=(
            "For adults, acetaminophen 650 mg may be administered orally every 6 hours "
            "as needed for fever of 100.4 F or higher. Do not exceed 3000 mg within "
            "24 hours."
        ),
        plain_text=(
            "Adults can take acetaminophen 650 mg by mouth every 6 hours if a fever "
            "reaches 100.4 F or higher. Do not take more than 3000 mg within 24 hours."
        ),
        source_name="MedlinePlus (NIH) — acetaminophen label basics, paraphrased",
        source_url="https://medlineplus.gov/druginfo/meds/a681004.html",
    ),
    CuratedCard(
        slug="wound-care-basics",
        category=HavenConcernCategory.MINOR_INJURY,
        title="Caring for a small cut",
        original_text=(
            "Keep the wound clean and dry for the first 24 hours. Do not remove the "
            "dressing during that period. Monitor for erythema, swelling, or warmth. "
            "If bleeding does not stop after 10 minutes of steady pressure, seek "
            "medical care."
        ),
        plain_text=(
            "Keep the cut clean and dry for the first 24 hours. Do not take the "
            "bandage off during that time. Watch for redness, swelling, or skin that "
            "feels warm. If bleeding does not stop after 10 minutes of steady "
            "pressure, get medical care."
        ),
        source_name="MedlinePlus (NIH) — cuts and puncture wounds, paraphrased",
        source_url="https://medlineplus.gov/ency/article/000043.htm",
    ),
    CuratedCard(
        slug="stomach-bug-hydration",
        category=HavenConcernCategory.STOMACH_TROUBLE,
        title="Staying hydrated during a stomach bug",
        original_text=(
            "For emesis or diarrhea, administer small, frequent sips of an oral "
            "rehydration solution. Avoid sugary beverages. If an infant has no wet "
            "diapers for 8 hours, or an adult has no urination for 12 hours, seek "
            "medical care."
        ),
        plain_text=(
            "If you are vomiting or have diarrhea, sip small amounts of an oral "
            "rehydration drink often. Avoid sugary drinks. If a baby has no wet "
            "diapers for 8 hours, or an adult has no urination for 12 hours, get "
            "medical care."
        ),
        source_name="MedlinePlus (NIH) — dehydration, paraphrased",
        source_url="https://medlineplus.gov/dehydration.html",
    ),
    CuratedCard(
        slug="antibiotic-course-instructions",
        category=HavenConcernCategory.MEDICATION_INSTRUCTIONS,
        title="Reading a prescription label",
        original_text=(
            "Take 1 tablet by mouth 2 times daily with food. Do not take on an empty "
            "stomach. Finish all 14 doses even if symptoms resolve sooner."
        ),
        plain_text=(
            "Take 1 tablet by mouth 2 times each day with food. Do not take it when "
            "your stomach is empty. Finish all 14 doses even if you feel better "
            "sooner."
        ),
        source_name="MedlinePlus (NIH) — taking medicines as directed, paraphrased",
        source_url="https://medlineplus.gov/ency/patientinstructions/000883.htm",
    ),
    CuratedCard(
        slug="cold-self-care-and-warning-signs",
        category=HavenConcernCategory.COUGH_OR_COLD,
        title="Colds: self-care and when to get help",
        original_text=(
            "Most colds resolve on their own within 7 to 10 days. Rest and "
            "maintain fluid intake. Call 911 for trouble breathing, blue lips, or "
            "chest pain — these are emergency warning signs."
        ),
        plain_text=(
            "Most colds get better on their own in 7 to 10 days. Rest and drink "
            "fluids. Call 911 right away for trouble breathing, blue lips, or chest "
            "pain — these are emergency warning signs."
        ),
        source_name="MedlinePlus (NIH) — common cold, paraphrased",
        source_url="https://medlineplus.gov/commoncold.html",
    ),
    CuratedCard(
        slug="stress-basics",
        category=HavenConcernCategory.STRESS_OR_ANXIETY,
        title="Everyday stress and where support lives",
        original_text=(
            "Feeling stressed or anxious is common. Slow breathing for 5 minutes can "
            "help in the moment. If worry keeps you from daily activities for 2 weeks "
            "or more, talk with a health professional. The 988 Lifeline provides free, "
            "confidential support."
        ),
        plain_text=(
            "Stress and anxious feelings are common. Try slow breathing for 5 minutes "
            "to help in the moment. If worry keeps you from daily activities for "
            "2 weeks or more, talk with a health professional. The 988 Lifeline "
            "offers free, confidential support."
        ),
        source_name="MedlinePlus (NIH) — stress, paraphrased",
        source_url="https://medlineplus.gov/stress.html",
    ),
)


def seed_haven_content(db: Session) -> None:
    """Idempotently upsert curated Haven resources and validated guidance cards."""

    for curated in CURATED_RESOURCES:
        resource_id = _stable_id("haven_resource", curated.slug)
        resource = db.get(HavenResource, resource_id)
        if resource is None:
            resource = HavenResource(id=resource_id, slug=curated.slug)
            db.add(resource)
        resource.name = curated.name
        resource.description = curated.description
        resource.url = curated.url
        resource.kind = curated.kind
        resource.jurisdiction = "US"
        resource.provenance = curated.provenance
        resource.source_mode = curated.source_mode
        resource.reviewed_on = _REVIEWED_ON
        resource.retrieved_on = _RETRIEVED_ON
        resource.review_valid_until = _REVIEW_VALID_UNTIL
        resource.is_available = True

    for card_def in CURATED_CARDS:
        violations = card_violations(card_def.original_text, card_def.plain_text)
        if violations:
            raise ValueError(f"Curated card {card_def.slug!r} failed validation: {violations}")
        card_id = _stable_id("haven_card", card_def.slug)
        card = db.get(HavenGuidanceCard, card_id)
        if card is None:
            card = HavenGuidanceCard(id=card_id, slug=card_def.slug)
            db.add(card)
        card.category = card_def.category
        card.title = card_def.title
        card.original_text = card_def.original_text
        card.plain_text = card_def.plain_text
        card.source_name = card_def.source_name
        card.source_url = card_def.source_url
        card.jurisdiction = "US"
        card.reviewed_on = _REVIEWED_ON

    db.flush()


def main() -> None:
    """Entry point for ``python -m zion_api.haven_seed``."""

    from zion_api.core.config import get_settings

    settings = get_settings()
    engine = get_engine(settings.database_url)
    with Session(engine) as db:
        seed_haven_content(db)
        db.commit()
    print("Seeded deterministic Haven curated content.")  # noqa: T201


if __name__ == "__main__":
    main()
