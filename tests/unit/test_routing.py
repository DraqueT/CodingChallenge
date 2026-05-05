from app.models.api import OrderRouteRequest
from app.repositories.fixtures import FixtureRepository
from app.services.routing import RoutingService


def build_service() -> RoutingService:
    return RoutingService(FixtureRepository())


def test_prefers_single_same_region_warehouse() -> None:
    service = build_service()

    response = service.route_order(
        OrderRouteRequest.model_validate(
            {
                "orderId": "ORD-100",
                "shippingDestination": {"region": "NORTHEAST"},
                "lineItems": [{"sku": "SKU-WIDGET-BLUE", "quantity": 3}],
            }
        )
    )

    assert response.status == "FULFILLED"
    assert response.fulfillment_plan[0].warehouse_id == "WH-EAST-1"


def test_prefers_higher_inventory_on_single_warehouse_tie() -> None:
    service = build_service()
    response = service.route_order(
        OrderRouteRequest.model_validate(
            {
                "orderId": "ORD-102",
                "shippingDestination": {"region": "MIDWEST"},
                "lineItems": [{"sku": "SKU-CABLE-USB-C", "quantity": 1}],
            }
        )
    )

    assert response.status == "FULFILLED"
    assert response.fulfillment_plan[0].warehouse_id == "WH-MIDWEST-1"


def test_returns_partial_with_insufficient_inventory() -> None:
    service = build_service()

    response = service.route_order(
        OrderRouteRequest.model_validate(
            {
                "orderId": "ORD-103",
                "shippingDestination": {"region": "NORTHEAST"},
                "lineItems": [{"sku": "SKU-GIZMO-GOLD", "quantity": 10}],
            }
        )
    )

    assert response.status == "PARTIALLY_FULFILLED"
    assert response.unfulfillable_items[0].reason == "INSUFFICIENT_INVENTORY"
    assert response.unfulfillable_items[0].quantity == 6


def test_uses_minimal_split_with_proximity_preference() -> None:
    service = build_service()

    response = service.route_order(
        OrderRouteRequest.model_validate(
            {
                "orderId": "ORD-101",
                "shippingDestination": {"region": "WEST"},
                "lineItems": [
                    {"sku": "SKU-GADGET-RED", "quantity": 20},
                    {"sku": "SKU-CHARGER-FAST", "quantity": 3},
                ],
            }
        )
    )

    assert response.status == "FULFILLED"
    assert sorted([entry.warehouse_id for entry in response.fulfillment_plan]) == sorted(["WH-SOUTH-2", "WH-WEST-1"])


def test_returns_sku_not_found() -> None:
    service = build_service()

    response = service.route_order(
        OrderRouteRequest.model_validate(
            {
                "orderId": "ORD-104",
                "shippingDestination": {"region": "SOUTHEAST"},
                "lineItems": [{"sku": "SKU-DOES-NOT-EXIST", "quantity": 1}],
            }
        )
    )

    assert response.status == "UNFULFILLABLE"
    assert response.fulfillment_plan == []
    assert response.unfulfillable_items[0].reason == "SKU_NOT_FOUND"


def test_prefers_single_warehouse_before_split() -> None:
    service = build_service()

    response = service.route_order(
        OrderRouteRequest.model_validate(
            {
                "orderId": "ORD-105",
                "shippingDestination": {"region": "WEST"},
                "lineItems": [
                    {"sku": "SKU-GADGET-GREEN", "quantity": 2},
                    {"sku": "SKU-CABLE-USB-C", "quantity": 2},
                ],
            }
        )
    )

    assert response.status == "FULFILLED"
    assert len(response.fulfillment_plan) == 1
    assert response.fulfillment_plan[0].warehouse_id == "WH-WEST-1"
