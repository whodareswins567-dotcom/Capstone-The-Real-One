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

## Project Structure

```text
backend/       FastAPI application, SQLite access, and automated tests (backend/tests/)
frontend/      Static HTML/CSS/JS user interface
doc/           High-level, low-level, architecture, and Confluence docs
plan/          Implementation plan and test plan
```
