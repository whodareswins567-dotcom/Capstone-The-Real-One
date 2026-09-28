# Inventory Management System

This is an inventory management system built with:

- Frontend: HTML, CSS, JavaScript
- Backend: FastAPI
- Database: SQLite3

The implementation supports basic item listing, creation, editing, deletion, and a low-stock filter.

## Run Locally

`requirements.txt` lists runtime dependencies only; `requirements-dev.txt` adds test-only dependencies (pytest, httpx, pytest-cov) on top of it.

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

The automated suite (`backend/tests/`) runs against an isolated temp SQLite DB and never touches `backend/inventory.db`. Outside of tests, the same isolation is available via env vars: `INVENTORY_DB_PATH` to point at a different DB file, and `INVENTORY_SEED_DB=0` to skip inserting the dev sample rows on startup.

CI (`.github/workflows/ci.yml`) runs this same `pytest -q` suite on every push and on pull requests targeting `main`, and reports pass/fail status on the PR.

## Project Structure

```text
backend/       FastAPI application, SQLite access, and automated tests (backend/tests/)
frontend/      Static HTML/CSS/JS user interface
doc/           High-level, low-level, architecture, and Confluence docs
plan/          Implementation plan and test plan
```
