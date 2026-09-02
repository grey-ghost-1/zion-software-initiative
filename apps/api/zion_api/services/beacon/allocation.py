"""Deterministic, explainable allocation heuristic for synthetic supplies.

This is a plain greedy priority heuristic, not an optimizer, and it makes no
optimality guarantee. It allocates synthetic inventory to synthetic zones in a
fixed, explainable order and enforces two invariants:

* conservation -- total allocated per item never exceeds inventory, and
* non-negativity -- no allocated or remaining quantity is ever below zero.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

ACTIVATION_SEVERITY = 2


class AllocationInvariantError(RuntimeError):
    """Raised if a computed allocation would violate a hard invariant."""


@dataclass(frozen=True)
class AllocationLine:
    zone_id: str
    item: str
    quantity: int
    reason: str

    def as_dict(self) -> dict[str, object]:
        return {
            "zone_id": self.zone_id,
            "item": self.item,
            "quantity": self.quantity,
            "reason": self.reason,
        }


@dataclass
class AllocationResult:
    lines: list[AllocationLine] = field(default_factory=list)
    unmet_demand: list[AllocationLine] = field(default_factory=list)
    remaining_inventory: dict[str, int] = field(default_factory=dict)

    @property
    def allocated_units(self) -> int:
        return sum(line.quantity for line in self.lines)

    @property
    def unmet_units(self) -> int:
        return sum(line.quantity for line in self.unmet_demand)


def propose_allocation(
    zones: list[dict[str, Any]],
    inventory: dict[str, int],
    demand: dict[str, dict[str, int]],
) -> AllocationResult:
    """Compute a deterministic greedy allocation with per-line explanations."""

    if any(quantity < 0 for quantity in inventory.values()):
        raise AllocationInvariantError("Inventory quantities must be non-negative.")

    result = AllocationResult(remaining_inventory=dict(sorted(inventory.items())))

    eligible = sorted(
        (zone for zone in zones if int(zone["severity"]) >= ACTIVATION_SEVERITY),
        key=lambda zone: (-int(zone["severity"]), -int(zone["population"]), str(zone["zone_id"])),
    )
    deferred = [zone for zone in zones if int(zone["severity"]) < ACTIVATION_SEVERITY]

    for zone in deferred:
        zone_id = str(zone["zone_id"])
        for item, requested in sorted(demand.get(zone_id, {}).items()):
            result.unmet_demand.append(
                AllocationLine(
                    zone_id=zone_id,
                    item=item,
                    quantity=int(requested),
                    reason=(
                        f"deferred: severity {zone['severity']} is below the "
                        f"activation threshold of {ACTIVATION_SEVERITY}"
                    ),
                )
            )

    for rank, zone in enumerate(eligible, start=1):
        zone_id = str(zone["zone_id"])
        for item, requested in sorted(demand.get(zone_id, {}).items()):
            requested_qty = int(requested)
            if requested_qty < 0:
                raise AllocationInvariantError("Demand quantities must be non-negative.")
            remaining = result.remaining_inventory.get(item, 0)
            granted = min(requested_qty, remaining)
            if granted > 0:
                result.remaining_inventory[item] = remaining - granted
                result.lines.append(
                    AllocationLine(
                        zone_id=zone_id,
                        item=item,
                        quantity=granted,
                        reason=(
                            f"priority rank {rank} (severity {zone['severity']}, "
                            f"population {zone['population']}): granted "
                            f"min(demand {requested_qty}, remaining {remaining})"
                        ),
                    )
                )
            shortfall = requested_qty - granted
            if shortfall > 0:
                result.unmet_demand.append(
                    AllocationLine(
                        zone_id=zone_id,
                        item=item,
                        quantity=shortfall,
                        reason=f"inventory exhausted for {item} after higher-priority zones",
                    )
                )

    _assert_invariants(inventory, result)
    return result


def _assert_invariants(inventory: dict[str, int], result: AllocationResult) -> None:
    allocated_per_item: dict[str, int] = {}
    for line in result.lines:
        if line.quantity < 0:
            raise AllocationInvariantError("Allocation lines must be non-negative.")
        allocated_per_item[line.item] = allocated_per_item.get(line.item, 0) + line.quantity

    for item, allocated in allocated_per_item.items():
        if allocated > inventory.get(item, 0):
            raise AllocationInvariantError(f"Allocation for {item} exceeds inventory.")

    if any(quantity < 0 for quantity in result.remaining_inventory.values()):
        raise AllocationInvariantError("Remaining inventory must be non-negative.")
