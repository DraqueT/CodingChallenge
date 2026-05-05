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
