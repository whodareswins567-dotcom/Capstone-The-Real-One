# Test Plan

## Goal

Provide a minimal automated regression baseline for the FastAPI backend so that core API behaviors are verified on every change, without relying on manual verification.

## Test Setup

- **Framework:** pytest + FastAPI `TestClient` (`httpx` under the hood).
- **Location:** `backend/tests/`.
- **Isolation:** `backend/tests/conftest.py` monkeypatches `database.DB_PATH` to a temporary SQLite file per test and sets `database.SEED_ON_STARTUP` to `False` before creating a fresh `TestClient`, so tests never read/write the dev database (`backend/inventory.db`) or depend on its sample rows. The same isolation is available outside tests via the `INVENTORY_DB_PATH` and `INVENTORY_SEED_DB=0` env vars (see `plan/implementation-plan.md`).
- **Fixtures:** `conftest.py` also provides a `create_item` fixture (a callable that POSTs a new item with sensible defaults, overridable via kwargs) shared across `test_items_crud.py`, `test_items_errors.py`, and `test_items_filters.py` to avoid duplicating item-creation boilerplate.
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
| Errors | `test_items_errors.py` | Duplicate SKU on create returns 409 with `detail="SKU already exists"`; PATCH/DELETE on a missing item returns 404 with `detail="Item not found"`; PATCH with no fields returns 400 with `detail="No fields provided"` |

## Out of Scope (for this baseline)

- Frontend/UI testing (no browser automation configured as part of this baseline).
- Load/performance testing.
- Concurrency/race-condition testing on SQLite writes.

## Future Follow-ups

- Add coverage for validation errors (e.g. missing required fields, invalid types) once the API's intentional validation gaps are resolved or explicitly documented as out of scope.
- Consider coverage reporting (`pytest-cov` is already a dependency) with a minimum threshold enforced in CI.
