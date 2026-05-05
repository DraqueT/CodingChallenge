import pytest
from pydantic import ValidationError

from app.models.api import OrderRouteRequest


def test_rejects_blank_order_id() -> None:
    with pytest.raises(ValidationError):
        OrderRouteRequest.model_validate(
            {
                "orderId": "   ",
                "shippingDestination": {"region": "NORTHEAST"},
                "lineItems": [{"sku": "SKU-WIDGET-BLUE", "quantity": 1}],
            }
        )


def test_rejects_duplicate_skus() -> None:
    with pytest.raises(ValidationError):
        OrderRouteRequest.model_validate(
            {
                "orderId": "ORD-1",
                "shippingDestination": {"region": "NORTHEAST"},
                "lineItems": [
                    {"sku": "SKU-WIDGET-BLUE", "quantity": 1},
                    {"sku": "SKU-WIDGET-BLUE", "quantity": 2},
                ],
            }
        )


def test_rejects_region_dne() -> None:
    with pytest.raises(ValidationError):
        OrderRouteRequest.model_validate(
            {
                "orderId": "ORD-1",
                "shippingDestination": {"region": "SOUTHNORTHERWEST"},
                "lineItems": [
                    {"sku": "SKU-WIDGET-BLUE", "quantity": 1},
                ],
            }
        )


def test_rejects_non_positive_quantities() -> None:
    with pytest.raises(ValidationError):
        OrderRouteRequest.model_validate(
            {
                "orderId": "ORD-1",
                "shippingDestination": {"region": "NORTHEAST"},
                "lineItems": [{"sku": "SKU-WIDGET-BLUE", "quantity": 0}],
            }
        )
