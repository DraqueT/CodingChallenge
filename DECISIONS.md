# Design Decisions & Tradeoffs

This document captures the implementation choices for the Order Routing Service.

## Architecture & Design

I used a small layered design:

- `app/api` handles HTTP routing and validation error serialization.
- `app/models` contains Pydantic request/response models and domain types like `Region`.
- `app/repositories` loads the provided JSON fixtures into an in-memory, read-only repository. Also contains some basic data access business logic, mimicking procedures which might be stored in a database.
- `app/services` contains the routing algorithm and all fulfillment planning logic.

This keeps the routing behavior independent from FastAPI so the important business logic can be tested directly with unit tests.

## Routing Logic

The routing service evaluates the rules in priority order:

1. First it checks whether any single warehouse can fulfill the entire order.
2. If more than one warehouse can do that, it ranks them first by destination proximity, then by requested warehouse of SKU's highest available inventory.
3. If no single warehouse can fulfill the order, it evaluates all warehouse subsets. Because there are only five warehouses in the fixture data, exhaustive subset search is simple and easy to reason about.
    - Note: I have a feeling this is a big pain point in terms of scalability as designed. This would be an early efficiency target.
4. Among subset candidates, it prefers the plan that fulfills the most units, then uses the fewest warehouses, then uses the closest warehouses, then uses the highest relevant inventory as a tiebreaker.

As noted above, the real tradeoff here is the subset planner. It's intentionally tuned for this exercise rather than a large, scalable production environment.

## Data Access

I chose not to use a database. The requirements explicitly allow in-memory loading, so inventory is read-only and order persistence is out of scope (though would not be difficult to implement). A fixture-backed repository gives the same shape as a real data access layer without adding migration or runtime setup complexity.

The data structures are modeled after header->line style logic within a database, and could be easily translated to a SQL environment. As noted elsewhere in this document, doing so would allow for significant optimizations.

The repository exposes a narrow read API:

- list all warehouses
- get inventory count of an SKU for a particular warehouse
- get total inventory for a SKU across all warehouses

That keeps the service layer decoupled from the fixture file format.

## Error Handling

Pydantic handles most validation:

- blank `orderId`
- invalid regions
- blank o invalid SKU values
- empty line items
- duplicate line items
- zero or negative quantities

I added a model-level check for duplicate SKUs because that rule is business-specific. FastAPI normally returns `422` validation errors, so I added a custom exception handler that converts request validation failures into the required `400 VALIDATION_ERROR` response shape.

For routing outcomes:

- blank `orderId` returns `VALIDATION_ERROR` with details of error
- missing or invalid regions return `VALIDATION_ERROR` with details of valid regions
- missing SKUs return `SKU_NOT_FOUND`
- empty line items returns `VALIDATION_ERROR` with details of error
- duplicate line items returns `VALIDATION_ERROR` with explanation of error
- shortfalls on known SKUs return `INSUFFICIENT_INVENTORY`
- orders with zero fulfilled units return `UNFULFILLABLE`



## Testing Strategy

I focused on behavior that carries the most risk:

- schema validation and duplicate SKU rejection
- fixture loading integrity
- single-warehouse preference
- regional proximity behavior
- split-fulfillment behavior
- inventory tiebreakers
- partial fulfillment and unfulfillable classification
- API-level success and validation responses

I did not add performance tests or broad fixture snapshots. For a take-home, targeted scenario tests provide more signal.

## Assumptions

- The proximity table in `REQUIREMENTS.md` does not fully rank all five regions on every row. I treated omitted regions as lowest preference and appended them to each destination's ranking.
- When no plan can fully satisfy the order, I maximize fulfilled units first, then minimize the number of warehouses, then apply proximity and inventory tiebreakers.
- Inventory is loaded once and treated as immutable for the lifetime of the process because the exercise describes the service as read-only.

## If I Had More Time...

- Add structured logging around routing decisions so warehouse selection is easier to debug.
- Replace the in-memory repository with a persistent data store and add repository contract tests.
- (Directly related to the above) Rework inefficient code/loops. Much of this could be mitigated by using SQL and offloading looping logic for things like addition row values, which currently would lead directly to scaling issues.
- Implement more secure practices:
    - Ensure that SQL injection is protected against.
    - Implement authentication on the basic requests.
    - Implement request throttling.
    - Implement bounding on request size and size of all fields within request.
    - More carefully audit responses (some raw Pydantic messaging comes back sometimes, and I'm sure other things leak back as well)
- Add metrics around unfulfillable rates, split shipments, and latency.
- Revisit the routing planner for larger warehouse counts with a more targeted search strategy.
