# CAP-36 Test Plan

This document defines the minimal automated test baseline required by CAP-36.

## Goals
- Provide a deterministic baseline of backend tests that can be run locally with one command.
- Cover core health and item listing behavior to avoid regressions.
- Avoid modifying non-test SQLite database state.

## Scope
### In Scope (MIN)
- API integration tests (FastAPI TestClient) for the backend:
  - `GET /api/health`
  - `GET /api/items`
- Test harness setup and fixtures.
- README update with test run instructions.

### Out of Scope (for CAP-36)
- Full end-to-end frontend EE2 automation.
- Full coverage for all item endpoints and edge cases.
m- CI pipeline integration (may be follow-up ticket).

## Test Types
- **Integration style API tests**: Use TestClient against the FastAPI app.
  - Assert status codes and minimal, stable JSON shapes.
  - Avoid brittle assertions (e.g. ordering of items).

## DB isolation strategy
- Tests should not rely on a developer local `backend/inventory.db` file.
- Preferred approach (fix later if needed):
  - Use a temporary SQLite database file path for tests, or override the DB path via env var.
- If the code does not support this off-the-bat, a small, minimal change to make DB path configurable is allowed in CAP-36 only if required to run tests.
  - (This ticket stated: "edit only if needed" for `backend/main.py`.)

## How to run tests
1. Install dependencies:
   ```bash
   pip install -r requirements.txt -r requirements-dev.txt
  ```
2. Run:
   ```bash
   pytest -q
   ```

## Pass/Fail Criteria
- All tests pass on a fresh clone following the documented steps.
 - Tests are deterministic and do not depend on existing DB state.
