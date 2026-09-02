"""Beacon allocation heuristic: determinism, conservation, non-negativity."""

from __future__ import annotations

import pytest

from zion_api.services.beacon.allocation import (
    AllocationInvariantError,
    propose_allocation,
)
from zion_api.services.beacon.fixtures import Scenario, load_fixture


def _inputs() -> tuple[list[dict[str, object]], dict[str, int], dict[str, dict[str, int]]]:
    fixture = load_fixture(Scenario.DEFAULT)
    return fixture["zones_table"], fixture["inventory"], fixture["demand"]


def test_allocation_is_deterministic() -> None:
    zones, inventory, demand = _inputs()

    first = propose_allocation(zones, inventory, demand)
    second = propose_allocation(zones, inventory, demand)

    assert [line.as_dict() for line in first.lines] == [line.as_dict() for line in second.lines]
    assert [line.as_dict() for line in first.unmet_demand] == [
        line.as_dict() for line in second.unmet_demand
    ]


def test_allocation_conserves_inventory_and_never_goes_negative() -> None:
    zones, inventory, demand = _inputs()

    result = propose_allocation(zones, inventory, demand)

    allocated: dict[str, int] = {}
    for line in result.lines:
        assert line.quantity >= 0
        allocated[line.item] = allocated.get(line.item, 0) + line.quantity
    for item, total in allocated.items():
        assert total <= inventory[item]
        assert result.remaining_inventory[item] == inventory[item] - total
    assert all(quantity >= 0 for quantity in result.remaining_inventory.values())


def test_highest_severity_zone_is_served_first_with_explanations() -> None:
    zones, inventory, demand = _inputs()

    result = propose_allocation(zones, inventory, demand)

    first_zone_lines = [line for line in result.lines if line.zone_id == "zone-a"]
    assert first_zone_lines, "zone-a (severity 5) must receive allocations"
    for line in result.lines:
        assert "priority rank" in line.reason
        assert "min(demand" in line.reason


def test_below_threshold_zones_are_deferred_with_a_reason() -> None:
    zones, inventory, demand = _inputs()

    result = propose_allocation(zones, inventory, demand)

    deferred = [line for line in result.unmet_demand if line.zone_id == "zone-d"]
    assert deferred
    assert all("below the activation threshold" in line.reason for line in deferred)
    assert not any(line.zone_id == "zone-d" for line in result.lines)


def test_shortfalls_are_reported_as_unmet_demand() -> None:
    zones, _inventory, demand = _inputs()
    scarce = {"water_kits": 10, "meal_packs": 0, "hygiene_kits": 0}

    result = propose_allocation(zones, scarce, demand)

    assert result.allocated_units == 10
    assert any("inventory exhausted" in line.reason for line in result.unmet_demand)
    assert result.remaining_inventory["water_kits"] == 0


def test_negative_inputs_are_rejected() -> None:
    zones, inventory, demand = _inputs()

    with pytest.raises(AllocationInvariantError):
        propose_allocation(zones, {"water_kits": -1}, demand)

    bad_demand = {"zone-a": {"water_kits": -5}}
    with pytest.raises(AllocationInvariantError):
        propose_allocation(zones, inventory, bad_demand)
