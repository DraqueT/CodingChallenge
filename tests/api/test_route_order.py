from fastapi.testclient import TestClient

from tests.conftest import create_client


def test_route_order_success() -> None:
    client = create_client()

    response = client.post(
        "/orders/route",
        json={
            "orderId": "ORD-200",
            "shippingDestination": {"region": "NORTHEAST"},
            "lineItems": [{"sku": "SKU-WIDGET-BLUE", "quantity": 3}],
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "FULFILLED"
    assert body["fulfillmentPlan"][0]["warehouseId"] == "WH-EAST-1"


def test_route_order_partial_fulfillment() -> None:
    client = create_client()

    response = client.post(
        "/orders/route",
        json={
            "orderId": "ORD-201",
            "shippingDestination": {"region": "WEST"},
            "lineItems": [{"sku": "SKU-GIZMO-GOLD", "quantity": 10}],
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "PARTIALLY_FULFILLED"
    assert body["unfulfillableItems"][0]["reason"] == "INSUFFICIENT_INVENTORY"


def test_route_order_validation_error() -> None:
    client = create_client()

    response = client.post(
        "/orders/route",
        json={
            "orderId": "ORD-202",
            "shippingDestination": {"region": "NORTHEAST"},
            "lineItems": [
                {"sku": "SKU-WIDGET-BLUE", "quantity": 1},
                {"sku": "SKU-WIDGET-BLUE", "quantity": 2},
            ],
        },
    )

    assert response.status_code == 400
    body = response.json()
    assert body["error"] == "VALIDATION_ERROR"
    assert body["details"][0]["field"] == ""
    assert body["message"] == "Value error, Duplicate SKUs are not allowed: SKU-WIDGET-BLUE"
