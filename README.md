# Inventory Management System

This is an inventory management system built with:

- Frontend: HTML, CSS, JavaScript
- Backend: FastAPI
- Database: SQLite3

The implementation supports basic item listing, creation, editing, deletion, and a low-stock filter.

## CORS configuration

The backend uses an environment-driven CORS (cross-origin request) allowlist.

- Env var: `IMS_CORS_ALLOW_ORIGINS`
- Format: comma-separated list of origins
- Safe default: if unset or empty, no origins are allowed (i.e. denied by default)

Example (local frontend at http://localhost:3000):

```bash
export IMS_CORS_ALLOW_ORIGINS="http://localhost:3000"
uvicorn backend.main:app --reload
```

## Run Locally

```bash
pip install -r requirements.txt
uvicorn backend.main:app --reload
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
