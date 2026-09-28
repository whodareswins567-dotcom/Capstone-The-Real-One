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

- Tests set the env var `INVENTORY_DB_PATH` to a temp file DB.
- Schema + seed are applied before in-process app client is created.

## CI (GitHub Actions)

- Workflow: `.github/workflows/ci.yml`
- Triggers: on `pull_request` to `main  and on `push` to any branch.