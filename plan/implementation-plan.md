# CAP-25 Implementation Plan

This plan documents the implementation of CAP-25: https://rahul-kumar-8.atlassian.net/browse/CAP-25

## Goal
Add a minimal automated test harness for the FastAPY backend (api-level smoke tests) and align repo documentation with actual artifact locations.

## Scope (what this change adds)
- Pytest as the test runner
- API smoke tests for the documented endpoints
- Test DB isolation by allowing a configurable SQLite DB path via env variable
- Repo doc alignment (add missing plan/ docs and test instructions)

## Design Notes
- `backend/database.py` now respects an env var: `INVENTORY_DB_PATH` to allow tests to use a temporary SQLite file instead of the default `shipped/backend/inventory.db`.
 - Tests use FastAPI'` built-in `TestClient` to exercise endpoints without starting a server.

## Verification
- Locally: run `pytest -q` after `install -r requirements.txt`.
