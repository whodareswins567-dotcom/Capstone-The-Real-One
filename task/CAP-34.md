# CAP-34 — Reconcile documented `plan/` artifacts with repository contents (add missing plans or update docs)

## Links
- **Jira:** https://rahul-kumar-8.atlassian.net/browse/CAP-34
- **PR:** https://github.com/whodareswins567-dotcom/Capstone-The-Real-One/pull/8
- **HLD:** _TBD_
- **LLD:** _TBD_

## Summary
Documentation and Confluence stated the repository contains a `plan/` directory with build notes, verification, and specific planning documents (implementation plan and test plan). The repo lacked `plan/`, causing documentation drift and onboarding friction.

CAP-34 restores `plan/` artifacts and updates references so the repo and docs are consistent.

## Acceptance Criteria
1. Repo default branch contains `plan/` with referenced planning artifacts **OR** docs no longer claim it exists and point to the correct location.
2. No references to non-existent `plan/` in `README.md`, `doc/confluence-ready.md`, and `doc/achievements-so-far.md`.
3. Confluence page “Inventory Management System – Achievements So Far” is consistent with the repo after the chosen resolution.
4. New developer can locate planning/testing guidance without dead paths.

## Implementation / Changes (from provided info)
- Added `plan/` artifacts (planning & verification guidance):
  - `plan/implementation-plan.md`
  - `plan/test-plan.md`
- Updated documentation to reference the plan artifacts:
  - `README.md`
  - `doc/confluence-ready.md`
  - `doc/achievements-so-far.md`

## Architecture Notes
### Components
**Existing**
- Static Frontend (`frontend/`) — HTML/CSS/JavaScript UI
- FastAPI Backend (`backend/main.py`) — serves UI + REST API
- DB layer (`backend/database.py`) — SQLite connection/init/seed
- Models (`backend/models.py`) — Pydantic schemas
- Documentation (`doc/`) — HLD/LLD/API docs

**Added (non-runtime)**
- Planning & verification artifacts (`plan/`) — Markdown plans for implementation/testing guidance

### Key data flows
- **Load inventory list**
  - Browser UI (`frontend/app.js`) → FastAPI `GET /api/items` → SQLite (`inventory_items`) → JSON → UI renders
- **Create / update / delete item**
  - UI form → FastAPI (`POST`/`PATCH`/`DELETE`) → Pydantic validation → SQLite write → JSON → UI updates
- **Engineering workflow: plan and verify**
  - Read README/doc → follow `plan/` files → run uvicorn → verify endpoints/UI per `plan/test-plan.md`

## Risks / Follow-ups
### Known risks
- **Doc accuracy regressions** (medium): PR diff suggests possible doc typos (e.g., accidental `m ` prefixes) and possible endpoint mismatch in the test plan (e.g., `/health` vs `/api/health`).
- **Confluence drift persists** (low-medium): Confluence pages may remain out of sync unless updated alongside merges.
- **No automated verification** (medium): still no CI-enforced checks; manual steps could be skipped.

### Recommended follow-ups
1. **High:** Review PR for doc typos and endpoint correctness; fix accidental prefixes and ensure test plan references actual routes.
2. **Medium:** Update Confluence “Achievements So Far” to link to repo `plan/` paths (or note location); if no permissions, add a note page elsewhere and link it.
3. **Medium:** Add minimal automated tests (pytest + FastAPI TestClient) and a GitHub Actions workflow.

## Notes / Updates
- 2026-09-28: Ticket file created; PR linked.
