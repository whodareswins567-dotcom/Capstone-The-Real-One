# Inventory Management System

This is an inventory management system built with:

- Frontend: HTML, CSS, JavaScript
- Backend: FastAPI
- Database: SQLite3

The implementation supports basic item listing, creation, editing, deletion, and a low-stock filter.

## Authentication & Roles (CAP-44)
Write endpoints require an API key and a role. Read endpoints remain public.

### Required headers (for write endpoints)
- `X-API-Key`: must match the env var `INVENTORY_API_KEY`
- `X-User-Role`: one of:
  - `inventory_operator`
  - `supervisor`
  - `administrator`

### Permissions (write endpoints)
- POST `/api/items`: inventory_operator, supervisor, administrator
- PATCH `/api/items/{id}`: inventory_operator, supervisor, administrator
- DELETE `/api/items/{id}`: supervisor, administrator

## Run Locally

```bash
pip install -r requirements.txt
INVENTORY_API_KEY=your-dev-key uvicorn backend.main:app --reload
```

Open:
```text
http://127.0.0.1:8000
```

API docs:
```text
http://127.0.0.1:8000/docs
```

## Testing

```bash
pip install -r requirements.txt -r requirements-dev.txt
pytest -q
```

CI runs `pytest -q` directly (not `python -m pytest`), so `pytest.ini` pins
`pythonpath = .` and `testpaths = tests` — otherwise `tests/conftest.py`'s
`import backend.database` fails to resolve under a bare `pytest` invocation,
and discovery could pick up stray test-like files outside `tests/`.

## Project Structure

```text
backend/   FastAPI application and SQLite access
frontend/  Static HTML/CSS/JS user interface
doc/       High-level, low-level, architecture, and Confluence docs
tests/     Automated tests
```
