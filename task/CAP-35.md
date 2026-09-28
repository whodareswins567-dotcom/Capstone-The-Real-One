# CAP-35 — Add automated tests and CI for the FastAPI backend

## Links
- **Jira:** https://rahul-kumar-8.atlassian.net/browse/CAP-35
- **PR:** https://github.com/whodareswins567-dotcom/Capstone-The-Real-One/pull/9
- **HLD:** _TBD_
- **LLD:** _TBD_

## Summary
The backend currently relies on initial/manual verification, which increases regression risk as the system evolves. The FastAPI service includes multiple behaviors (CRUD, search filtering, low-stock filtering, uniqueness conflicts, and not-found handling) that are easy to break without noticing.

CAP-35 adds a minimal automated test suite and runs it in CI on every push/PR.

## Acceptance Criteria
1. Core API test coverage exists: health check, CRUD operations, search filter behavior, low-stock filter behavior, and error cases (HTTP 409 on duplicate SKU, HTTP 404 on missing item for update/delete).
2. Search filtering is verified: `GET /api/items` with `search` parameter returns filtered results matching `sku`, `name`, or `category`.
3. Low-stock filtering is verified: `GET /api/items` with `low_stock` enabled returns only items with `quantity <= reorder_level`.
4. Duplicate SKU conflict is verified: creating/updating with duplicate SKU returns HTTP 409 and `detail="SKU already exists"`.
5. Not-found behavior is verified: update/delete for missing item returns HTTP 404 and `detail="Item not found"`.
6. CI runs tests on change: CI pipeline installs dependencies, runs tests, and fails if tests fail.

## Implementation / Changes (from provided info)
### New components
- **Backend integration tests** (`backend/tests/`) using **pytest + FastAPI TestClient**
- **CI workflow** (GitHub Actions expected under `.github/workflows/`) to run pytest on push/PR
- **DB path override seam** via environment variable `INVENTORY_DB_PATH` so tests use an isolated SQLite DB

### Changed files (reported)
- `backend/database.py` — DB_PATH now reads `INVENTORY_DB_PATH` env var (defaults to `backend/inventory.db`)
- `requirements.txt` — added `pytest` and `httpx`
- `backend/tests/conftest.py` — fixtures set `INVENTORY_DB_PATH` to a temp DB and create TestClient; reloads backend modules
- `backend/tests/test_health.py` — validates `GET /api/health` returns 200 and `{ "status": "ok" }`
- `backend/tests/test_items_crud.py` — CRUD tests for `/api/items`
- `backend/tests/test_items_filters.py` — tests `search` and `low_stock` filters
- `backend/tests/test_items_errors.py` — tests duplicate SKU (409) and missing item (404)
- `.github/.gitkeep` — placeholder file (workflow file not visible in the provided file list snippet)

## Architecture Notes
### Components
**Existing**
- FastAPI backend (`backend/main.py`) — REST API serving inventory endpoints
- SQLite database layer (`backend/database.py`) — connection, schema init, seed data
- Frontend static app (`frontend/`) — HTML/CSS/JS

**Added (non-runtime)**
- pytest-based backend integration tests (`backend/tests/`)
- CI workflow to run tests (GitHub Actions)
- Config seam for test DB (`INVENTORY_DB_PATH`)

### Data flows
- **CI verification flow (PR/push)**
  1. Developer push / GitHub PR
  2. GitHub Actions runner
  3. Install dependencies (`pip install -r requirements.txt`)
  4. Run `pytest`
  5. Tests call API via FastAPI TestClient (in-process)
  6. Backend reads/writes SQLite using temp DB path from `INVENTORY_DB_PATH`

- **API integration test flow**
  1. pytest test case
  2. TestClient request (`/api/health`, `/api/items`, etc.)
  3. FastAPI handler
  4. DB access via `backend/database.py`
  5. SQLite read/write
  6. HTTP response asserted by tests

## Risks / Follow-ups
### Known risks
- **High:** Filter test SKU typos/inconsistencies may cause CI failure (e.g., `SEARKH` vs `SEARCH`; `LOW-STOKK` vs `LOW-STOCK`).
- **Medium:** Import-time DB_PATH coupling — DB path is bound at import time in `backend/database.py`; tests rely on env var being set before import and may need module reloads.
- **Medium:** CI not enforced by branch protection — if status checks aren’t required on `main`, failing tests won’t block merge.

### Recommended follow-ups
1. **High:** Fix SKU typos/inconsistencies in `backend/tests/test_items_filters.py` so created SKUs match asserted SKUs; rerun CI.
2. **High:** Ensure CI workflow file is under `.github/workflows/` and triggers on `pull_request` and `push`; verify checks appear on PR.
3. **Medium:** Enable branch protection on `main` requiring CI checks to pass before merge.
4. **Low:** Consider refactoring DB path resolution to be runtime-configurable (config object/dependency injection) to reduce import-time coupling.

## Checklist
- [ ] HLD link added
- [ ] LLD link added
- [ ] PR merged
- [ ] CI passing on PR

## Notes / Updates
- 2026-09-28: Ticket file created; Jira + PR + Confluence notes link captured.
- Confluence doc: https://rahul-kumar-8.atlassian.net/wiki/spaces/DEV/pages/2260993/CAP-35+Automated+Tests+CI+for+FastAPI+Backend+Architecture+Notes
