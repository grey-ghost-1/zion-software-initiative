"""Harbor matching, safety, RBAC, workflow, audit, and capacity tests."""

from __future__ import annotations

import threading
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker

from zion_api.core.errors import HarborConflictError
from zion_api.db.base import Base
from zion_api.models.harbor import (
    AccessibilityRequirement,
    AccessibilityStatus,
    CapacityFreshness,
    Eligibility,
    HarborCapacity,
    HarborNeed,
    HarborPlan,
    HarborResource,
    HarborVolunteerAvailability,
    HarborZone,
    NeedCategory,
    NeedStatus,
    NeedUrgency,
    PlanStatus,
    ResourceStatus,
    TriageDecision,
)
from zion_api.models.organization import Organization
from zion_api.seed import DEMO_PASSWORD, seed_demo_data
from zion_api.services.harbor import approve_plan


def _login(client: TestClient, email: str) -> str:
    response = client.post("/auth/login", json={"email": email, "password": DEMO_PASSWORD})
    assert response.status_code == 200
    return str(response.json()["access_token"])


def _headers(client: TestClient, email: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {_login(client, email)}"}


def _resource(db: Session, code: str) -> HarborResource:
    resource = db.scalar(select(HarborResource).where(HarborResource.code == code))
    assert resource is not None
    return resource


def _need(db: Session, ref: str) -> HarborNeed:
    need = db.scalar(select(HarborNeed).where(HarborNeed.request_ref == ref))
    assert need is not None
    return need


def _new_need_payload(ref: str = "DEMO-NEW-401") -> dict[str, object]:
    return {
        "request_ref": ref,
        "category": "food",
        "zone": "central",
        "quantity": 2,
        "eligibility": "open_access",
        "accessibility_requirement": "none",
        "urgency": "standard",
    }


def test_matching_is_explainable_and_rejections_cover_unsafe_capacity_states(
    seeded_client: TestClient, seeded_db_session: Session
) -> None:
    headers = _headers(seeded_client, "visitor@zion.example")
    shelter_need = _need(seeded_db_session, "DEMO-SHELTER-200")

    missing = HarborResource(
        organization_id=shelter_need.organization_id,
        code="RES-MISSING-CAPACITY",
        name="Missing Capacity Synthetic Shelter",
        category=NeedCategory.TEMPORARY_SHELTER,
        zone=HarborZone.NORTH,
        eligibility=Eligibility.COORDINATOR_REFERRAL,
        accessibility=AccessibilityStatus.STEP_FREE,
        status=ResourceStatus.OPEN,
    )
    unknown_access = HarborResource(
        organization_id=shelter_need.organization_id,
        code="RES-UNKNOWN-ACCESS",
        name="Unknown Access Synthetic Shelter",
        category=NeedCategory.TEMPORARY_SHELTER,
        zone=HarborZone.NORTH,
        eligibility=Eligibility.COORDINATOR_REFERRAL,
        accessibility=AccessibilityStatus.UNKNOWN,
        status=ResourceStatus.OPEN,
    )
    seeded_db_session.add_all([missing, unknown_access])
    seeded_db_session.flush()
    seeded_db_session.add(
        HarborCapacity(
            resource_id=unknown_access.id,
            organization_id=shelter_need.organization_id,
            total_units=4,
            reserved_units=0,
            fulfilled_units=0,
            freshness=CapacityFreshness.CURRENT,
        )
    )
    seeded_db_session.commit()

    response = seeded_client.get(
        f"/harbor/zion-demo/needs/{shelter_need.id}/matches", headers=headers
    )

    assert response.status_code == 200
    body = response.json()
    assert body["protected_traits_used"] is False
    assert body["matches"][0]["resource"]["code"] == "RES-NORTH-SHELTER"
    assert {part["rule"] for part in body["matches"][0]["score_components"]} == {
        "need_category",
        "eligibility",
        "coarse_zone",
        "open_status",
        "capacity_freshness",
        "available_capacity",
        "accessibility",
    }
    rejected = {
        item["resource"]["code"]: set(item["rejected_reasons"]) for item in body["rejected"]
    }
    assert "capacity_stale" in rejected["RES-CENTRAL-STALE-BEDS"]
    assert "capacity_insufficient" in rejected["RES-SOUTH-FULL-BEDS"]
    assert "capacity_missing" in rejected["RES-MISSING-CAPACITY"]
    unknown = next(
        item for item in body["matches"] if item["resource"]["code"] == "RES-UNKNOWN-ACCESS"
    )
    assert any("accessibility is unknown" in note for note in unknown["uncertainty"])


def test_closed_and_unknown_capacity_never_become_available(
    seeded_client: TestClient, seeded_db_session: Session
) -> None:
    headers = _headers(seeded_client, "visitor@zion.example")
    transit_need = _need(seeded_db_session, "DEMO-TRANSIT-300")
    response = seeded_client.get(
        f"/harbor/zion-demo/needs/{transit_need.id}/matches", headers=headers
    )
    closed = next(
        item
        for item in response.json()["rejected"]
        if item["resource"]["code"] == "RES-SOUTH-TRANSIT"
    )
    assert "resource_closed" in closed["rejected_reasons"]

    resources = seeded_client.get("/harbor/zion-demo/resources", headers=headers).json()["items"]
    unknown = next(item for item in resources if item["code"] == "RES-CENTRAL-SUPPLIES")
    assert unknown["capacity"]["freshness"] == "unknown"
    assert unknown["capacity"]["available_units"] is None


def test_role_boundaries_and_cross_organization_isolation(seeded_client: TestClient) -> None:
    visitor = _headers(seeded_client, "visitor@zion.example")
    volunteer = _headers(seeded_client, "volunteer@zion.example")
    alliance_admin = _headers(seeded_client, "admin@alliance.zion.example")

    assert seeded_client.get("/harbor/zion-demo/needs", headers=visitor).status_code == 200
    denied = seeded_client.post(
        "/harbor/zion-demo/needs", headers=visitor, json=_new_need_payload()
    )
    assert denied.status_code == 403
    assert seeded_client.get("/harbor/zion-demo/needs", headers=volunteer).status_code == 403
    plans = seeded_client.get("/harbor/zion-demo/volunteer-plans", headers=volunteer)
    assert plans.status_code == 200
    cross_org = seeded_client.get("/harbor/zion-demo/needs", headers=alliance_admin)
    assert cross_org.status_code == 404
    assert cross_org.json()["error"]["code"] == "organization_not_found"


def test_create_rejects_duplicate_unknown_and_unbounded_input(seeded_client: TestClient) -> None:
    headers = _headers(seeded_client, "coordinator@zion.example")
    payload = _new_need_payload()
    assert (
        seeded_client.post("/harbor/zion-demo/needs", headers=headers, json=payload).status_code
        == 201
    )
    duplicate = seeded_client.post("/harbor/zion-demo/needs", headers=headers, json=payload)
    assert duplicate.status_code == 409
    assert duplicate.json()["error"]["code"] == "harbor_conflict"

    invalid = dict(payload, request_ref="<script>alert(1)</script>", quantity=99)
    invalid["private_notes"] = "unrestricted text is not accepted"
    response = seeded_client.post("/harbor/zion-demo/needs", headers=headers, json=invalid)
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"


def test_workflow_requires_approval_and_updates_audit_capacity_and_metrics(
    seeded_client: TestClient, seeded_db_session: Session
) -> None:
    headers = _headers(seeded_client, "coordinator@zion.example")
    created = seeded_client.post(
        "/harbor/zion-demo/needs", headers=headers, json=_new_need_payload("DEMO-FLOW-501")
    )
    assert created.status_code == 201
    need_id = created.json()["id"]
    pantry = _resource(seeded_db_session, "RES-CENTRAL-PANTRY")

    matches = seeded_client.get(
        f"/harbor/zion-demo/needs/{need_id}/matches", headers=headers
    ).json()
    assert matches["matches"][0]["resource"]["id"] == pantry.id

    triage = seeded_client.post(
        f"/harbor/zion-demo/needs/{need_id}/triage",
        headers=headers,
        json={
            "decision": "ready",
            "reason": "coordinator_override",
            "selected_resource_id": pantry.id,
        },
    )
    assert triage.status_code == 200
    selected_availability = seeded_db_session.scalar(
        select(HarborVolunteerAvailability).where(
            HarborVolunteerAvailability.category == NeedCategory.FOOD
        )
    )
    assert selected_availability is not None
    proposal = seeded_client.post(
        f"/harbor/zion-demo/needs/{need_id}/plans",
        headers=headers,
        json={
            "resource_id": pantry.id,
            "volunteer_availability_id": selected_availability.id,
        },
    )
    assert proposal.status_code == 201
    plan_id = proposal.json()["id"]

    premature = seeded_client.post(
        f"/harbor/zion-demo/plans/{plan_id}/fulfill", headers=headers
    )
    assert premature.status_code == 409
    before = seeded_db_session.get(HarborCapacity, pantry.id)
    assert before is not None
    reserved_before = before.reserved_units

    approved = seeded_client.post(
        f"/harbor/zion-demo/plans/{plan_id}/approve", headers=headers
    )
    assert approved.status_code == 200
    seeded_db_session.refresh(before)
    assert before.reserved_units == reserved_before + 2

    fulfilled = seeded_client.post(
        f"/harbor/zion-demo/plans/{plan_id}/fulfill", headers=headers
    )
    assert fulfilled.status_code == 200
    assert fulfilled.json()["status"] == "fulfilled"
    seeded_db_session.refresh(before)
    assert before.reserved_units == reserved_before
    assert before.fulfilled_units == 5

    audit = seeded_client.get(
        f"/harbor/zion-demo/needs/{need_id}/audit", headers=headers
    ).json()
    assert [item["action"] for item in audit["items"]] == [
        "harbor.need_created",
        "harbor.need_triaged",
        "harbor.plan_proposed",
        "harbor.plan_approved_capacity_reserved",
        "harbor.plan_fulfilled",
    ]
    assert all("actor_user_id" not in item for item in audit["items"])

    metrics = seeded_client.get("/harbor/zion-demo/metrics", headers=headers).json()
    assert metrics["total_requests"] == 4
    assert metrics["fulfilled_requests"] == 1
    assert metrics["awaiting_approval"] == 0
    assert "Synthetic demonstration data only" in metrics["synthetic_disclosure"]

    volunteer = _headers(seeded_client, "volunteer@zion.example")
    assignment = seeded_client.get(
        "/harbor/zion-demo/volunteer-plans", headers=volunteer
    ).json()["items"][0]
    assert set(assignment) == {
        "id",
        "need_id",
        "request_ref",
        "resource_id",
        "resource_name",
        "resource_zone",
        "category",
        "quantity",
        "volunteer_code",
        "status",
        "proposed_at",
        "approved_at",
        "fulfilled_at",
        "synthetic",
    }


def test_protected_attributes_are_absent_from_input_and_scoring_contract(
    seeded_client: TestClient,
) -> None:
    schema = seeded_client.get("/openapi.json").json()
    properties = schema["components"]["schemas"]["HarborNeedCreate"]["properties"]
    forbidden = {
        "age",
        "race",
        "ethnicity",
        "gender",
        "religion",
        "disability",
        "immigration_status",
        "benefit_status",
        "medical_details",
    }
    assert forbidden.isdisjoint(properties)

    headers = _headers(seeded_client, "visitor@zion.example")
    needs = seeded_client.get("/harbor/zion-demo/needs", headers=headers).json()["items"]
    result = seeded_client.get(
        f"/harbor/zion-demo/needs/{needs[0]['id']}/matches", headers=headers
    ).json()
    all_rules = {
        part["rule"]
        for candidate in result["matches"] + result["rejected"]
        for part in candidate["score_components"]
    }
    assert forbidden.isdisjoint(all_rules)


def test_database_constraint_rejects_direct_overbooking(
    seeded_db_session: Session,
) -> None:
    capacity = seeded_db_session.get(
        HarborCapacity, _resource(seeded_db_session, "RES-NORTH-SHELTER").id
    )
    assert capacity is not None
    capacity.reserved_units = capacity.total_units
    capacity.fulfilled_units = 1
    with pytest.raises(IntegrityError):
        seeded_db_session.commit()
    seeded_db_session.rollback()


def test_concurrent_approvals_cannot_overbook_sqlite(tmp_path: Path) -> None:
    database_url = f"sqlite:///{tmp_path / 'harbor-race.db'}"
    engine = create_engine(
        database_url, connect_args={"check_same_thread": False, "timeout": 10}
    )
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine, expire_on_commit=False)
    with session_factory() as setup:
        seed_demo_data(setup)
        setup.commit()
        organization = setup.scalar(
            select(Organization).where(Organization.slug == "zion-demo")
        )
        assert organization is not None
        resource = _resource(setup, "RES-CENTRAL-PANTRY")
        capacity = setup.get(HarborCapacity, resource.id)
        volunteer = setup.scalar(select(HarborVolunteerAvailability))
        assert capacity is not None and volunteer is not None
        capacity.total_units = 1
        capacity.reserved_units = 0
        capacity.fulfilled_units = 0
        plan_ids: list[str] = []
        for index in range(2):
            need = HarborNeed(
                organization_id=organization.id,
                request_ref=f"DEMO-RACE-60{index}",
                category=NeedCategory.FOOD,
                zone=HarborZone.CENTRAL,
                quantity=1,
                eligibility=Eligibility.OPEN_ACCESS,
                accessibility_requirement=AccessibilityRequirement.NONE,
                urgency=NeedUrgency.STANDARD,
                status=NeedStatus.PROPOSED,
                triage_decision=TriageDecision.READY,
            )
            setup.add(need)
            setup.flush()
            plan = HarborPlan(
                organization_id=organization.id,
                need_id=need.id,
                resource_id=resource.id,
                volunteer_availability_id=volunteer.id,
                quantity=1,
                status=PlanStatus.PROPOSED,
            )
            setup.add(plan)
            setup.flush()
            plan_ids.append(plan.id)
        setup.commit()
        organization_id = organization.id
        resource_id = resource.id

    barrier = threading.Barrier(2)
    results: list[str] = []
    result_lock = threading.Lock()

    def attempt(plan_id: str) -> None:
        with session_factory() as session:
            barrier.wait()
            try:
                approve_plan(
                    session,
                    organization_id=organization_id,
                    plan_id=plan_id,
                    actor_user_id="synthetic-race-actor",
                )
                result = "approved"
            except HarborConflictError:
                result = "conflict"
            with result_lock:
                results.append(result)

    threads = [threading.Thread(target=attempt, args=(plan_id,)) for plan_id in plan_ids]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=15)

    assert sorted(results) == ["approved", "conflict"]
    with session_factory() as check:
        final_capacity = check.get(HarborCapacity, resource_id)
        assert final_capacity is not None
        assert final_capacity.reserved_units == 1
    engine.dispose()
