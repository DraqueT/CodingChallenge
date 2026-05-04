# Requirements: Order Routing Service

## Business Context

Our fulfillment network consists of multiple warehouses distributed across U.S. regions. Each warehouse maintains its own inventory. When a customer places an order, the system must determine a **fulfillment plan** — an assignment of each line item to a specific warehouse for picking, packing, and shipping.

The goal is to minimize shipping cost and time while ensuring we can fulfill as much of the order as possible.

---

## API Specification

### `POST /orders/route`

Accepts an order and returns a fulfillment plan.

#### Request Body

```json
{
  "orderId": "ORD-12345",
  "shippingDestination": {
    "region": "NORTHEAST"
  },
  "lineItems": [
    {
      "sku": "SKU-WIDGET-BLUE",
      "quantity": 3
    },
    {
      "sku": "SKU-GADGET-RED",
      "quantity": 1
    }
  ]
}
```

| Field | Type | Required | Description |
|---|---|---|---|
| `orderId` | string | yes | Unique identifier for the order |
| `shippingDestination.region` | string | yes | One of: `NORTHEAST`, `SOUTHEAST`, `MIDWEST`, `WEST`, `SOUTHWEST` |
| `lineItems` | array | yes | One or more items to fulfill |
| `lineItems[].sku` | string | yes | Product SKU |
| `lineItems[].quantity` | integer | yes | Quantity requested (must be > 0) |

#### Success Response — `200 OK`

```json
{
  "orderId": "ORD-12345",
  "status": "FULFILLED",
  "fulfillmentPlan": [
    {
      "warehouseId": "WH-EAST-1",
      "items": [
        { "sku": "SKU-WIDGET-BLUE", "quantity": 3 },
        { "sku": "SKU-GADGET-RED", "quantity": 1 }
      ]
    }
  ],
  "unfulfillableItems": []
}
```

#### Partial Fulfillment Response — `200 OK`

When some items cannot be fulfilled due to insufficient inventory across all warehouses:

```json
{
  "orderId": "ORD-12345",
  "status": "PARTIALLY_FULFILLED",
  "fulfillmentPlan": [
    {
      "warehouseId": "WH-EAST-1",
      "items": [
        { "sku": "SKU-WIDGET-BLUE", "quantity": 2 }
      ]
    }
  ],
  "unfulfillableItems": [
    { "sku": "SKU-WIDGET-BLUE", "quantity": 1, "reason": "INSUFFICIENT_INVENTORY" },
    { "sku": "SKU-GADGET-RED", "quantity": 1, "reason": "SKU_NOT_FOUND" }
  ]
}
```

#### Validation Error Response — `400 Bad Request`

```json
{
  "error": "VALIDATION_ERROR",
  "message": "Line item quantity must be greater than zero",
  "details": [
    { "field": "lineItems[0].quantity", "issue": "Must be > 0" }
  ]
}
```

---

## Routing Rules

The routing engine must apply the following rules **in priority order**:

### Rule 1: Single-Warehouse Preference

If any single warehouse can fulfill the **entire** order, prefer that over splitting. Fulfilling from one warehouse reduces shipping costs and simplifies logistics.

### Rule 2: Regional Proximity

Among warehouses that can fulfill the order (or the largest portion of it), prefer the warehouse in the **same region** as the shipping destination. If no warehouse is in the same region, use the following proximity map:

| Destination | 1st preference | 2nd preference | 3rd preference | 4th preference |
|---|---|---|---|---|
| NORTHEAST | NORTHEAST | SOUTHEAST | MIDWEST | WEST |
| SOUTHEAST | SOUTHEAST | NORTHEAST | MIDWEST | SOUTHWEST |
| MIDWEST | MIDWEST | NORTHEAST | SOUTHEAST | WEST |
| WEST | WEST | SOUTHWEST | MIDWEST | NORTHEAST |
| SOUTHWEST | SOUTHWEST | WEST | MIDWEST | SOUTHEAST |

### Rule 3: Minimize Split Shipments

When no single warehouse can fulfill the entire order, split across the **fewest warehouses possible**. Among options with the same number of warehouses, prefer the combination whose warehouses are closest to the destination (per the proximity map above).

### Rule 4: Inventory Tiebreaker

When multiple warehouses are equally suitable (same region, same coverage), prefer the warehouse with the **highest available inventory** for the requested SKUs. This helps distribute fulfillment load and avoids draining one warehouse.

---

## Edge Cases to Handle

| Scenario | Expected Behavior |
|---|---|
| SKU not found in any warehouse | Include in `unfulfillableItems` with reason `SKU_NOT_FOUND` |
| Insufficient total inventory across all warehouses | Fulfill what you can; list remainder in `unfulfillableItems` with reason `INSUFFICIENT_INVENTORY` |
| All items unfulfillable | Return status `UNFULFILLABLE` with empty `fulfillmentPlan` |
| Duplicate SKUs in line items | Reject with `400` validation error |
| Empty line items array | Reject with `400` validation error |
| Missing or blank `orderId` | Reject with `400` validation error |
| Invalid region value | Reject with `400` validation error |
| Quantity is zero or negative | Reject with `400` validation error |

---

## Data Model Reference

The seed data includes the following entities. You are free to model these however you see fit in your application — this is just a reference for the shape of the data.

**Warehouses**

Each warehouse has an ID, a display name, and a region.

**Inventory**

Each inventory record ties a SKU to a warehouse with a current available quantity.

---

## Out of Scope

The following are **not** required for this exercise:

- Authentication or authorization
- Inventory mutation (the routing service is read-only against inventory)
- Order persistence (you do not need to store orders; just process and respond)
- Asynchronous processing or queuing
- Multiple shipping addresses per order
