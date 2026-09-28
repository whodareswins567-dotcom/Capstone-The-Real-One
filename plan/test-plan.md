# Test Plan

## Goal

Provide a minimal automated regression baseline for the FastAPI backend so that core API behaviors are verified on every change, without relying on manual verification.

## Test Setup

- **Framework:** pytest + FastAPI `TestClient` (`httpx` under the hood).
- **Location:** `backend/tests/`.
- **Isolation:** `backend/tests/conftest.py` points `INVENTORY_DB_PATH` at a temporary SQLite file per test session and creates a fresh `TestClient`, so tests never read/write the dev database (`backend/inventory.db`).
- **Run locally:**

  ```bash
  pip install -r requirements.txt -r requirements-dev.txt
  pytest -q
  ```

- **Run in CI:** `.github/workflows/ci.yml` installs dependencies and runs `pytest -q` on every push and PR to `main`.

## Coverage

| Area | File | Cases |
|------|------|-------|
| Health | `test_health.py` | `GET /api/health` returns 200 with `{"status": "ok"}` |
| CRUD | `test_items_crud.py` | Create, list, partial update (PATCH), delete of an item |
| Filters | `test_items_filters.py` | `search` matches SKU/name/category; `low_stock=true` returns only items where `quantity <= reorder_level` |
| Errors | `test_items_errors.py` | Duplicate SKU on create returns 409 with `detail="SKU already exists"`; PATCH/DELETE on a missing item returns 404 with `detail="Item not found"` |

## Out of Scope (for this baseline)

- Frontend/UI testing (no browser automation configured as part of this baseline).
- Load/performance testing.
- Concurrency/race-condition testing on SQLite writes.

## Future Follow-ups

- Add coverage for validation errors (e.g. missing required fields, invalid types) once the API's intentional validation gaps are resolved or explicitly documented as out of scope.
- Consider coverage reporting (`pytest-cov` is already a dependency) with a minimum threshold enforced in CI.
