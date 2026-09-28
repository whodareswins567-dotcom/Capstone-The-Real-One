# CAP-42 Implementation Plan

This document exists to reconcile the repo documentation with the actual repo structure, and to capture the implementation choices for CAP-42.

## Goals

- Add automated tests for core backend FastAPI endpoints (health, items CRUD).
- Add CI (GitHub Actions) to run `pytest -q` on PRs.
- Resolve docs mismatches about a missing `plan/` folder.

## Approach

- Tests are implemented with `pytest` and FastAPI's `TestClient`.
- Tests use an isolated SQLite database per test run (file backed in `tmp_path`).
  - `backend/main.py` exposes a `create_app(db_path)` factory. The db path is
    stored on `app.state.db_path` and threaded through `init_db()`/`seed_db()`
    (lifespan) and route handlers (via the `get_db_connection` FastAPI
    dependency), instead of being read from an env var at call time.
  - The test fixture (`tests/conftest.py`) calls `create_app(db_path=...)`
    directly with a `tmp_path` file, so isolation is guaranteed by
    dependency injection rather than by import order or process env vars.
  - `backend.database.get_db_path()` still reads `INVENTORY_DB_PATH` (falling
    back to `backend/inventory.db`) for the default `app = create_app()`
    instance used outside tests.

## Files touched

- `backend/database.py`: `get_connection()`/`init_db()`/`seed_db()` accept an
  optional explicit `db_path`, bypassing `get_db_path()`/env var when given.
- `backend/main.py`: `create_app(db_path)` factory + `get_db_connection`
  dependency, replacing the module-level `app`/inline `get_connection()` calls.
- `tests/*`: add tests and fixtures.
- `.github/workflows/ci.yml`: Run tests on PRs.
