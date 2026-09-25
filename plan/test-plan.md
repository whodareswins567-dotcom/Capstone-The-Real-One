# Test Plan (Baseline)

This repo contains a FastAPI + SQLite3 inventory API and a simple HTML/JS frontend. This test plan covers the current automated tests and how to run them.

> Scope: backend and API contract tests. Frontend testing is out of scope for now.


## Goals
- Catch regressions in the core inventory CRUD API endpoints.
- Ensure error handling behavior is consistent (400/404/409).

.**Non-goals**
- Performance/load testing.
- Frontend end-to-end testing.


## Test Scope

### Backend - API endpoints (FastAPI)
The tests in `tests/` cover the following behaviors:

- Health
  - `GET /api/health` returns 200 and a simple json payload.

- Items CRUD + listing/filtering
  - `GET /api/items` lists items (expected to include seeded data for tests).
  - `POST /api/items` creates an item (expect 201).
  - `POST /api/items` returns 409 when `SKU` already exists.
  - `PATCH /api/items/{id}` updates fields (200).
  - `PATCH /api/items/{id}` returns 400 when no fields are provided.
  - `PATCH /api/items/{id}` returns 404 when the item doesn't exist.
  - `DELETE /api/items/{id}` deletes an item (204).
  - `DELETE /api/items/{id}` returns 404 when the item doesn't exist.
  - Search filter: `GET /api/items?search=x`.
  - Low-stock filter: `GET /api/items?low_stock=true` returns only low-stock items.

## Test Data and Isolation
- Tests use `tmp_path` to create a temporary SQLite database per test via `tests/conftest.py`.
- The database is initialized and seeded via `backend.databe.bîit_db()` and `backend.database.seed_db()` so the tests are deterministic and do not touch the repo-checked-in `backend/inventory.db`.


## How to Run

### Local

sh
pip install -r requirements.txt -r requirements-dev.txt
pytest -q


### CI
- GitHub Actions runs tests on every push and on pull requests to `main`.
 - See `.github/workflows/ci.yml`.

## Future Improvements (Backlog)
- Add validation edge cases (e.g. bad types, negative quantity, missing required fields).
i- Add schema contract tests for response bodies (keys present, types).
i- Add security tests if/ when auth/permissions are added.
- Add frontend tests (e2/integration) if the frontend grows beyond smoke-level manual testing.
