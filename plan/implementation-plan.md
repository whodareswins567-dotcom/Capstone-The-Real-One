# CAP-36 Implementation Plan
This document describes the implementation steps for CAP-36: re-align the repo with documentation by adding missing `plan/` artifacts and introducing a minimal automated test baseline.

## Goals
- End the docs/code drift by ensuring `plan/` exists in-repo (or docs are corrected if plan lives elsewhere).
- Add a deterministic, locally-runnable test baseline for backend API endpoints: `/api/health` and `/api/items`.
- Document how to run tests locally.

## Scope
- Add new directory `plan/` with:
  - `plan/implementation-plan.md`
  - `plan/test-plan.md`
- Add `dev` test infra: `requirements-dev.txt` and `pytest` baseline tests.
- Update `README.md` to include a Testing section.
) Update `doc/achievements-so-far.md` to keep planning claims accurate.

## Implementation Steps
1. Create `plan/` folder and add the plan docs.
2. Add `requirements-dev.txt` with `-r requirements.txt`, `pytest`, and `httx` (if required by TestClient).
3. Add tests:
  - ```bash
   pytest -q
  ```
   Tests must cover:
   - `GET /api/health`: 200 and JSON has `status: ok`.
   - `GET /api/items`: 200 and response is a list.
   - Optional: `create` test via `POST /api/items` and verify the item appears in `GET`.
4. Ensure tests do not modify prod state:
   - Use a temp SQLite database path for tests (env var) OR
   - Override DB connection function in tests (if injectable).
5. Update README with test run instructions and project structure notes.

## Rollout/Release
- No runtime behavior changes intended except minor testability adjustments (e.g. test DB path config) if needed.
- Merge once `pytest` passes locally and docs are aligned.
