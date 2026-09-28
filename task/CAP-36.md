# CAP-36 — Add missing plan/ artifacts and introduce minimal automated test baseline

## Links
- **Jira:** https://rahul-kumar-8.atlassian.net/browse/CAP-36
- **PR:** https://github.com/whodareswins567-dotcom/Capstone-The-Real-One/pull/10
- **HLD:** https://rahul-kumar-8.atlassian.net/wiki/spaces/Architecur/pages/393392/High+Level+Design
- **LLD:** _TBD_

## Summary
Project documentation (repo docs and Confluence) stated that planning/verification documents exist under a `plan/` folder (including an implementation plan and test plan) and that the project is ready for “expanded testing”. The repository structure did not include a `plan/` directory, indicating documentation/codebase drift.

**Objective:** Re-align the repository with documented structure by adding missing `plan/` artifacts (or correcting documentation if they live elsewhere) and introduce a minimal automated test baseline to reduce regression risk for core API behaviors (at minimum `/api/health` and `/api/items`).

## Acceptance Criteria
1. Plan artifacts aligned: a `plan/` directory exists or repo/Confluence documentation is updated to accurately state where the plan artifacts are stored.
2. Plan documents present (if `plan/` is the chosen source of truth): `plan/implementation-plan.md` and `plan/test-plan.md` are present in version control and readable.
3. Minimal automated test baseline exists: automated tests covering at least `/api/health` endpoint response behavior and `/api/items` endpoint behavior (at minimum: basic success path for list/create or equivalent).
4. Test execution instructions: clear instructions for how to run the automated tests locally (e.g., command(s) and any setup prerequisites) are present in project documentation.

## Notes / Updates
- PR opened: https://github.com/whodareswins567-dotcom/Capstone-The-Real-One/pull/10
- Repo changes include: `plan/` docs added, `requirements-dev.txt`, `backend/tests/` pytest suite, and DB path seam via `INVENTORY_DB_PATH`.

## Checklist
- [ ] HLD reviewed/linked
- [ ] LLD linked
- [ ] PR merged
- [ ] Tests passing (`pytest`)
- [ ] Docs aligned (README + doc/achievements-so-far.md)
