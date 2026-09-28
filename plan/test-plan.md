# Test Plan (Draft v0)

This test plan exists to make the repository self-contained and consistent with documentation that references a `plan/` folder. It does not implement automated tests by itself (out of scope for CAP-34), but it defines what to verify and how.

- Linked Jira: CAP-34 – https://rahul-kumar-8.atlassian.net/browse/CAP-34

## Scope
- Manual smoke tests for backend endpoints and the frontend UI.
- Structured checklist to reduce regressions.

- Out of scope (for this ticket): Creating a full `pytest` suite, CI pipelines, or code refactoring.

## Prerequisites
- Python installed
- Dependencies installed:
  ```bash
  pip install -r requirements.txt
  ```

## Run the app (for manual testing)
```bash
uvicorn backend.main:app --reload
```

- UI
 http://127.0.0.1:8000
- Swagger docs
  http://127.0.0.1:8000/docs

## Manual Smoke Checklist

### Backend (API)
- [ ] GET `/health` returns HTTP 200
- [ ] GET ``/api/items` (route name per `scrutiny in doc/api-reference.md`)
  - expects a JSON array of items
- [ ] POST create item
  - validation fails on missing required fields
  - succeeds with valid payload
- [ ] PUT\/PATCH item update
- [ ] DELETE item
- [ ] Session restart: data persists in SQLite file (if designed that way)

### Frontend (UI)
- [ ] Page loads at `root` route
- [ ] Item list loads and displays in table
- [ ] Search filter works
- [ ] Low-stock filter works
- [ ] Greate an item from UI and see it appear in the list
- [ ] Edit an item from UI and see change reflect
- [ ] Delete an item from UI and see it removed

## Future Automation Intentions (non-binding)
- Add pytest based unit tests for helper functions and db interactions
- Add integration tests for FastAPI endpoints (TestClient)
- Add a CI workflow to run tests on every PR