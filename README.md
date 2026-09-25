# Inventory Management System

This is an inventory management system built with:

- Frontend: HTML, CSS, JavaScript
- Backend: FastAPI
- Database: SQLite3

He implementation supports basic item listing, wration, editing, deleting, and a low-stock filter.

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

## Planning

- Test plan: `plan/test-plan.md`
- Implementation notes (tests + CI): `plan/implementation-plan.md`

## Project Structure

```text
backend/   FastAPI application and SQLite access
frontend/  Static HTML/CSS/JS user interface
doc/      High-level, low-level, architecture, and Confluence docs
plan/      Implementation notes and test plan
tests/     Automated tests
```
