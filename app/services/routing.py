from dataclasses import dataclass
from itertools import combinations

from app.models.api import (
    FulfillmentPlanEntry,
    FulfillmentPlanItem,
    OrderLineItem,
    OrderRouteRequest,
    OrderRouteResponse,
    UnfulfillableItem,
)
from app.models.domain import FulfillmentStatus, Region, UnfulfillableReason, Warehouse
from app.repositories.fixtures import FixtureRepository


# order indicates preferred proximity
PROXIMITY_MAP: dict[Region, list[Region]] = {
    Region.NORTHEAST: [
        Region.NORTHEAST,
        Region.SOUTHEAST,
        Region.MIDWEST,
        Region.WEST,
        Region.SOUTHWEST,
    ],
    Region.SOUTHEAST: [
        Region.SOUTHEAST,
        Region.NORTHEAST,
        Region.MIDWEST,
        Region.SOUTHWEST,
        Region.WEST,
    ],
    Region.MIDWEST: [
        Region.MIDWEST,
        Region.NORTHEAST,
        Region.SOUTHEAST,
        Region.WEST,
        Region.SOUTHWEST,
    ],
    Region.WEST: [
        Region.WEST,
        Region.SOUTHWEST,
        Region.MIDWEST,
        Region.NORTHEAST,
        Region.SOUTHEAST,
    ],
    Region.SOUTHWEST: [
        Region.SOUTHWEST,
        Region.WEST,
        Region.MIDWEST,
        Region.SOUTHEAST,
        Region.NORTHEAST,
    ],
}


@dataclass(frozen=True)
class WarehousePlan:
    warehouse: Warehouse
    items: tuple[tuple[str, int], ...]


@dataclass(frozen=True)
class CandidatePlan:
    warehouse_plans: tuple[WarehousePlan, ...]
    fulfilled_by_sku: dict[str, int]
    fulfilled_units: int
    warehouse_count: int
    proximity_score: tuple[int, ...]
    inventory_score: int


class RoutingService:
    def __init__(self, repository: FixtureRepository) -> None:
        self.repository = repository

    def route_order(self, order: OrderRouteRequest) -> OrderRouteResponse:
        line_items = order.line_items
        total_requested_units = sum(item.quantity for item in line_items)

        single_warehouse_plan = self._single_warehouse_plan(
            destination=order.shipping_destination.region,
            warehouses=self.repository.all_warehouses(),
            line_items=line_items,
        )

        if single_warehouse_plan is not None:
            fulfillment_plan = self._serialize_plan(single_warehouse_plan.warehouse_plans)
            unfulfillable_items = self._build_unfulfillable_items(line_items, single_warehouse_plan.fulfilled_by_sku)
            return OrderRouteResponse(
                orderId=order.order_id,
                status=self.fulfill_status_for(single_warehouse_plan.fulfilled_units, total_requested_units),
                fulfillmentPlan=fulfillment_plan,
                unfulfillableItems=unfulfillable_items,
            )

        best_plan = self._best_split_plan(
            destination=order.shipping_destination.region,
            warehouses=self.repository.all_warehouses(),
            line_items=line_items,
        )
        fulfillment_plan = self._serialize_plan(best_plan.warehouse_plans)
        unfulfillable_items = self._build_unfulfillable_items(line_items, best_plan.fulfilled_by_sku)
        return OrderRouteResponse(
            orderId=order.order_id,
            status=self.fulfill_status_for(best_plan.fulfilled_units, total_requested_units),
            fulfillmentPlan=fulfillment_plan,
            unfulfillableItems=unfulfillable_items,
        )

    # Find best matching warehouse for a given set of line items
    def _single_warehouse_plan(
        self,
        destination: Region,
        warehouses: list[Warehouse],
        line_items: list[OrderLineItem],
    ) -> CandidatePlan | None:
        candidates: list[CandidatePlan] = []

        for warehouse in warehouses:
            items: list[tuple[str, int]] = []
            fulfills_all = True
            inventory_score = 0
            for line_item in line_items:
                available = self.repository.warehouse_sku_count(warehouse.id, line_item.sku)
                inventory_score += available
                if available < line_item.quantity:
                    fulfills_all = False
                    break
                items.append((line_item.sku, line_item.quantity))

            if fulfills_all:
                candidates.append(
                    CandidatePlan(
                        warehouse_plans=(WarehousePlan(warehouse=warehouse, items=tuple(items)),),
                        fulfilled_by_sku={item.sku: item.quantity for item in line_items},
                        fulfilled_units=sum(item.quantity for item in line_items),
                        warehouse_count=1,
                        proximity_score=(self._region_rank(destination, warehouse.region),),
                        inventory_score=inventory_score,
                    )
                )

        if not candidates:
            return None

        # return highest ranked order (preference importance desc)
        return min(
            candidates,
            key=lambda plan: (
                plan.proximity_score,
                -plan.inventory_score,
                plan.warehouse_plans[0].warehouse.id,
            ),
        )

    def _best_split_plan(
        self,
        destination: Region,
        warehouses: list[Warehouse],
        line_items: list[OrderLineItem],
    ) -> CandidatePlan:
        candidates: list[CandidatePlan] = []

        # this is a inefficient and would not scale well: current sku location metadata stored/updated could help here
        for subset_size in range(1, len(warehouses) + 1):
            for subset in combinations(warehouses, subset_size):
                candidate = self._plan_for_subset(destination, list(subset), line_items)
                candidates.append(candidate)

        # return highest ranked order (preference importance desc)
        return min(
            candidates,
            key=lambda plan: (
                -plan.fulfilled_units,  # first to ensure preference for fulfilling entire order above all else
                plan.warehouse_count,
                plan.proximity_score,
                -plan.inventory_score,
                tuple(entry.warehouse.id for entry in plan.warehouse_plans),
            ),
        )

    def _plan_for_subset(
        self,
        destination: Region,
        warehouses: list[Warehouse],
        line_items: list[OrderLineItem],
    ) -> CandidatePlan:
        ranked_warehouses = sorted(
            warehouses,
            key=lambda warehouse: (
                self._region_rank(destination, warehouse.region),
                -self._warehouse_inventory_score(warehouse.id, line_items),
                warehouse.id,
            ),
        )

        allocations: dict[str, list[tuple[str, int]]] = {warehouse.id: [] for warehouse in ranked_warehouses}
        fulfilled_by_sku: dict[str, int] = {}

        for line_item in line_items:
            remaining = line_item.quantity
            fulfilled = 0
            for warehouse in ranked_warehouses:
                if remaining == 0:
                    break
                available = self.repository.warehouse_sku_count(warehouse.id, line_item.sku)
                if available <= 0:
                    continue
                allocated = min(available, remaining)
                allocations[warehouse.id].append((line_item.sku, allocated))
                remaining -= allocated
                fulfilled += allocated
            fulfilled_by_sku[line_item.sku] = fulfilled

        warehouse_plans = tuple(
            WarehousePlan(warehouse=warehouse, items=tuple(allocations[warehouse.id]))
            for warehouse in ranked_warehouses
            if allocations[warehouse.id]
        )
        used_warehouses = []
        for plan in warehouse_plans:
            used_warehouses.append(plan.warehouse)

        # used as tie breaker
        inventory_score = sum(
            self._warehouse_inventory_score(warehouse.id, line_items) for warehouse in used_warehouses
        )

        return CandidatePlan(
            warehouse_plans=warehouse_plans,
            fulfilled_by_sku=fulfilled_by_sku,
            fulfilled_units=sum(fulfilled_by_sku.values()),
            warehouse_count=len(used_warehouses),
            proximity_score=tuple(
                self._region_rank(destination, warehouse.region) for warehouse in used_warehouses
            ),
            inventory_score=inventory_score,
        )

    def _warehouse_inventory_score(self, warehouse_id: str, line_items: list[OrderLineItem]) -> int:
        return sum(self.repository.warehouse_sku_count(warehouse_id, item.sku) for item in line_items)

    @classmethod
    def _region_rank(cls, destination: Region, warehouse_region: Region) -> int:
        return PROXIMITY_MAP[destination].index(warehouse_region)

    @classmethod
    def _serialize_plan(cls, warehouse_plans: tuple[WarehousePlan, ...]) -> list[FulfillmentPlanEntry]:
        serialized_plans = []
        for plan in warehouse_plans:
            items = []
            for sku, quantity in plan.items:
                items.append(FulfillmentPlanItem(sku=sku, quantity=quantity))
            serialized_plans.append(FulfillmentPlanEntry(
                warehouseId=plan.warehouse.id,
                items=items
            ))
        return serialized_plans

    def _build_unfulfillable_items(
        self,
        line_items: list[OrderLineItem],
        fulfilled_by_sku: dict[str, int],
    ) -> list[UnfulfillableItem]:
        unfulfillable_items: list[UnfulfillableItem] = []
        for line_item in line_items:
            fulfilled_quantity = fulfilled_by_sku.get(line_item.sku, 0)
            if fulfilled_quantity >= line_item.quantity:
                continue
            reason = (
                UnfulfillableReason.SKU_NOT_FOUND
                if self.repository.total_inventory_for(line_item.sku) == 0
                else UnfulfillableReason.INSUFFICIENT_INVENTORY
            )
            unfulfillable_items.append(
                UnfulfillableItem(
                    sku=line_item.sku,
                    quantity=line_item.quantity - fulfilled_quantity,
                    reason=reason,
                )
            )
        return unfulfillable_items

    @classmethod
    def fulfill_status_for(cls, fulfilled_units: int, total_requested_units: int) -> FulfillmentStatus:
        if fulfilled_units == 0:
            return FulfillmentStatus.UNFULFILLABLE
        if fulfilled_units == total_requested_units:
            return FulfillmentStatus.FULFILLED
        return FulfillmentStatus.PARTIALLY_FULFILLED
