from typing import Annotated

from pydantic import BaseModel, Field, field_validator, model_validator

from app.models.domain import FulfillmentStatus, Region, UnfulfillableReason


PositiveQuantity = Annotated[int, Field(gt=0)]


class ShippingDestination(BaseModel):
    region: Region


class OrderLineItem(BaseModel):
    sku: str
    quantity: PositiveQuantity

    @field_validator("sku")
    @classmethod
    def validate_sku(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("SKU must not be blank")
        return value


class OrderRouteRequest(BaseModel):
    order_id: str = Field(alias="orderId")
    shipping_destination: ShippingDestination = Field(alias="shippingDestination")
    line_items: list[OrderLineItem] = Field(alias="lineItems", min_length=1)

    model_config = {"populate_by_name": True}

    @field_validator("order_id")
    @classmethod
    def validate_order_id(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("orderId must not be blank")
        return value

    @model_validator(mode="after")
    def validate_unique_skus(self) -> "OrderRouteRequest":
        seen: set[str] = set()
        duplicates: list[str] = []
        for item in self.line_items:
            if item.sku in seen:
                duplicates.append(item.sku)
            seen.add(item.sku)

        if duplicates:
            duplicate_list = ", ".join(sorted(set(duplicates)))
            raise ValueError(f"Duplicate SKUs are not allowed: {duplicate_list}")

        return self


class FulfillmentPlanItem(BaseModel):
    sku: str
    quantity: int


class FulfillmentPlanEntry(BaseModel):
    warehouse_id: str = Field(alias="warehouseId")
    items: list[FulfillmentPlanItem]

    model_config = {"populate_by_name": True}


class UnfulfillableItem(BaseModel):
    sku: str
    quantity: int
    reason: UnfulfillableReason


class OrderRouteResponse(BaseModel):
    order_id: str = Field(alias="orderId")
    status: FulfillmentStatus
    fulfillment_plan: list[FulfillmentPlanEntry] = Field(alias="fulfillmentPlan")
    unfulfillable_items: list[UnfulfillableItem] = Field(alias="unfulfillableItems")

    model_config = {"populate_by_name": True}


class ValidationErrorDetail(BaseModel):
    field: str
    issue: str


class ValidationErrorResponse(BaseModel):
    error: str
    message: str
    details: list[ValidationErrorDetail]
