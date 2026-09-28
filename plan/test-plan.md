# CAP-42 Test Plan

## Local Test Run

```bash
pip install -r requirements.txt -r requirements-dev.txt
pytest -q
```

## Test Categories

1. Health check
  - `GET /api/health` expects `200 + {"status":"ok"}`.

2. Items API
  - CRUD happy path: create → list (and/or search) → PATCH → delete.
  - Error/edge cases:
    - duplicate SKU → 409
    - PATCH missing item → 404
    - PATCH empty payload → 400

## Database Isolation

- `backend.main.create_app(db_path)` builds a FastAPI app pinned to an explicit
  SQLite path via `app.state.db_path`, injected into route handlers through the
  `get_db_connection` dependency.
- The `client` fixture (`tests/conftest.py`) calls `create_app(db_path=<tmp_path>/...)`
  directly, so each test gets an isolated DB by construction - not by setting an
  env var before import, and not dependent on import order.

## CI (GitHub Actions)

- Workflow: `.github/workflows/ci.yml`
- Triggers: `pull_request` targeting `main`, and `push` to `main`.
