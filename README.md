# Order Routing Service — Take-Home Exercise

## Overview

We're an eCommerce company that operates a network of warehouses across the United States. When a customer places an order, we need to determine which warehouse(s) should fulfill it. This decision depends on what's in stock, where the customer is located, and a set of business rules that optimize for cost and speed.

Your task is to build an **Order Routing Service** — a REST API that accepts an incoming order and returns a fulfillment plan.

## Time Expectation

We respect your time. Please spend roughly **3–4 hours** on this exercise. We're not looking for production-ready deployment infrastructure — we're looking at how you think about design, structure, and tradeoffs. If you run out of time, document what you would have done next in `DECISIONS.md`.

## Getting Started

### Choose Your Stack

Use whatever language, framework, and database you're most productive in. We care about your design thinking, not a specific technology. The only requirement is that your solution exposes a REST API.

### Seed Data

We've provided seed data in two formats for convenience:

- **`data/seed.sql`** — SQL statements to create and populate the database tables. Compatible with SQLite, PostgreSQL, MySQL, or similar. Adapt as needed for your chosen database.
- **`data/fixtures.json`** — The same data in JSON format. Use this if you prefer to load data programmatically or use a non-SQL datastore.

You're free to load this data however makes sense for your stack — a startup script, a migration tool, an ORM seed file, or even hardcoded in-memory for simplicity.

## What We Provide

| File | Purpose |
|---|---|
| `REQUIREMENTS.md` | Full specification — API contracts, routing rules, and edge cases |
| `data/seed.sql` | Database schema and seed data (SQL format) |
| `data/fixtures.json` | Seed data (JSON format) |
| `DECISIONS.md` | Template for you to document your design decisions and tradeoffs |

## What We're Looking For

- **Domain modeling** — How do you represent warehouses, inventory, orders, and fulfillment plans?
- **Separation of concerns** — Is routing logic cleanly separated from API and data access layers?
- **Extensibility** — Could a new routing rule be added without rewriting existing logic?
- **Error handling** — How does the service behave when inputs are invalid or orders can't be fulfilled?
- **Testing** — Do your tests cover the interesting scenarios?
- **Security considerations** — Input validation, defensive coding, safe handling of edge cases.

We are **not** evaluating:

- Choice of language or framework
- CI/CD configuration
- Production deployment setup
- Performance optimization (though thoughtful comments about it are welcome)
- UI or frontend work

## Submission

1. Create a new branch named `solution/<your-name>`.
2. Implement your solution, committing as you normally would (we appreciate seeing your progression).
3. Include a brief note in your README or `DECISIONS.md` on how to build and run your solution.
4. Fill out `DECISIONS.md`.
5. Open a pull request against `main` when you're done.

## Questions?

If anything in the requirements is ambiguous, make a reasonable assumption and document it in `DECISIONS.md`. This is intentional — we want to see how you handle ambiguity.
