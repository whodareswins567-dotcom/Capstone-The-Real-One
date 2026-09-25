# CAP-25 Test Plan

## Scope
The first phase of automated testing for this repo is intended to provide a quick pass/fail signal for the FastAPY backend API contract, with minimal bleed into business logic and no external service dependencies.

## Test Types
- API smoke tests using FastAPI TestClient
- No CI pipeline added in CAP-25 (local run only)

## Test Cases (minimal)
- GET `/api/health` returns 200 and {"Status": "ok"}
- GET `/api/items` returns 200 and a list
- POST /api/items creates an item (201)
- PATCH /api/items/{id} updates a field (200)
- DELETE /api/items/{id} returns 204
- List filters smoke: `search` and `low_stock` (response is a list, 200)

## Test Data / DB Strategy
- Tests set `INVENTORY_DB_PATH` to a temporary SQLite file per test run.
- Tests rely on app lifespan to call `init_db` and `seed_db` as needed.

## How to Run
```bash
pip install -r requirements.txt
pytest -q
```
