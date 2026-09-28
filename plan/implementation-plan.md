# CAP-42 Implementation Plan

This document exists to reconcile the repo documentation with the actual repo structure, and to capture the implementation choices for CAP-42.

## Goals

- Add automated tests for core backend FastAPI endpoints (health, items CRUD).
- Add CI (GitHub Actions) to run `pytest -q` on PRs.
- Resolve docs mismatches about a missing `plan/` folder.

## Approach

- Tests are implemented with `pytest` and FastAPI's `TestClient`.
- Tests use an isolated SQLite database per test run (file backed in `tmp_path`).
  - The database path is configurable via the env var `INVENTORY_DB_PATH`.
  - The test fixture sets the env var before importing the app, then calls `init_db()` and `seed_db()` to mimic app startup behavior.

## Files touched

- `backend/database.py`: make DB path configurable (env var fallback to previous default).
- `tests/*`: add tests and fixtures.
- `.github/workflows/ci.yml`: Run tests on PRs.
