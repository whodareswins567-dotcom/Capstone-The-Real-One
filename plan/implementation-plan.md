# Implementation Plan

## Scope

Inventory management system: static HTML/CSS/JS frontend served by a FastAPI backend backed by SQLite3. Supports listing (with search/low-stock filter), creating, editing, and deleting inventory items.

## Components

- **Backend (`backend/`)**
  - `main.py` — FastAPI app, routes, static file mount, startup lifecycle.
  - `database.py` — SQLite connection factory, schema creation, dev seed data. DB path is overridable via the `INVENTORY_DB_PATH` env var (used by tests to isolate state).
  - `models.py` — Pydantic request/response schemas.
- **Frontend (`frontend/`)** — Static HTML/CSS/JS, talks to `/api/items` via `fetch`.
- **Tests (`backend/tests/`)** — pytest suite using FastAPI's `TestClient`, run against an isolated temp SQLite DB per test session.

## Endpoints

| Method | Path              | Purpose                          |
|--------|-------------------|-----------------------------------|
| GET    | `/api/health`     | Liveness check                    |
| GET    | `/api/items`      | List items, optional `search` / `low_stock` filters |
| POST   | `/api/items`      | Create item                       |
| PATCH  | `/api/items/{id}` | Partial update                    |
| DELETE | `/api/items/{id}` | Delete item                       |

## Build Steps (completed)

1. Backend scaffolding: FastAPI app, SQLite schema + seed data, Pydantic models.
2. Frontend scaffolding: static table UI wired to the REST API.
3. Documentation: architecture, high/low-level design, API reference.
4. Test seam: `INVENTORY_DB_PATH` override so tests never touch the dev DB (`backend/inventory.db`).
5. Automated test baseline (`backend/tests/`): health check, CRUD, search/low-stock filters, error cases (409 duplicate SKU, 404 not found).
6. CI: run `pytest` on push/PR (see `.github/workflows/ci.yml`).
7. `plan/` artifacts (this file and `plan/test-plan.md`) added to align the repo with what the docs already described.

## Out of Scope

- Authentication/authorization.
- Multi-user concurrency handling beyond SQLite's defaults.
- Pagination for `/api/items` (not implemented; not currently planned).
