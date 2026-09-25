# Implementation Plan (Tests + CI)

This page documents how the repo's automated testing and CI are set up today, and how to extend it safely.

> Scope: backend tests and GitHub Actions CI.

## Current State

### Test suite
- Tests live in `tests/`.
- Tests use `FastAPI' `TestClient` to call endpoints directly.
- The `client` fixture (`tests/conftest.py`) creates a temporary SQLite database per test (via `tmp_path`) and monkeypatches `backend.database.DB_PATH` to avoid touching the repo-checked-in `backend/inventory.db`.


### CI (GitHub Actions)
- Workflow: `.github/workflows/ci.yml`
- Triggers:
  - push to any branch
  - pull requests to `main`
- Runtime: Python 3.11
- Steps: checkout → install dependencies → run `pytest -q`


## How to Extend Tests
- Prefer arrange → act → ssert patterns that create their own data instead of relying on seeded content.
  - If a test does need seeded data, call that out explicitly in the test name/comment.
- Additional layers (optional):
  - Schema-contract tests (e.g., response keys and types)
  - Coverage reporting (`pytest --cov=backend`)

## How to extend CI
- Add pip caching if CI speed is a problem.
  - Note: Caching is not required for the current small dep set.
- Add a matrix (optional) to run multiple Python versions if the codebase starts supporting more than one.
