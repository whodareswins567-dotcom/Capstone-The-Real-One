# CAP-37 — Establish automated API test suite and CI execution for backend

## Links
- **Jira:** https://rahul-kumar-8.atlassian.net/browse/CAP-37
- **PR:** https://github.com/whodareswins567-dotcom/Capstone-The-Real-One/pull/11
- **HLD:** _TBD_
- **LLD:** _TBD_
- **Design doc (Confluence):** https://rahul-kumar-8.atlassian.net/wiki/spaces/DEV/pages/2392065/CAP-37+Automated+API+Testing+CI+Architecture+HLD+LLD

## Summary
Add automated backend API tests and ensure CI executes them. Enable SQLite DB path override via `INVENTORY_DB_PATH` so tests can run against an isolated DB without affecting developer data. Add pytest tooling.

## Acceptance Criteria
- Test framework in place; runnable via a single command documented.
- CRUD tests exist (create/list/get/patch/delete).
- Search/filter tests exist (search and `low_stock`).
- Edge cases:
  - duplicate SKU returns **409** with detail `"SKU already exists"`
  - empty PATCH returns **400** with detail `"No fields provided"`
- Derived field `low_stock` computed correctly (`quantity <= reorder_level`).
- CI runs tests on PR/push and fails on test failures.

## Implementation notes (from PR + architecture summary)
- Repo already contained `tests/` and a CI workflow (`.github/workflows/ci.yml`) on `main` (per PR notes).
- PR #11 changes:
  - `backend/database.py`: DB path now respects `INVENTORY_DB_PATH`.
  - `requirements.txt`: added `pytest` and `pytest-cov`.

## Risks / Follow-ups
- **Runtime deps include test tooling** (pytest/pytest-cov in `requirements.txt`). Consider moving to `requirements-dev.txt` (or extras) to keep production/runtime installs minimal.
- **Import-time DB path**: `DB_PATH` derived at import time; tests must set env var before importing `backend.database` or could hit default DB.
- Verify CI installs the correct dependency set and executes pytest on `pull_request` + `push` to `main`.
- Optional: add coverage reporting / baseline threshold.

## Notes / Updates
- PR opened: https://github.com/whodareswins567-dotcom/Capstone-The-Real-One/pull/11
- Reviewer request failed due to permissions (specified user not a collaborator).

## Checklist
- [ ] Add HLD link
- [ ] Add LLD link
- [ ] PR merged
- [ ] CI green
- [ ] Follow-ups triaged (deps + lazy DB path)
