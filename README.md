# Inventory Management System

This is an inventory management system built with:

- Frontend: HTML, CSS, JavaScript
- Backend: FastAPI
- Database: SQLite3

The implementation supports basic item listing, creation, editing, deletion, and a low-stock filter.

## CORS configuration

The backend uses an environment-driven CORS (cross-origin request) allowlist.

- Env var: `IMS_CORS_ALLOW_ORIGINS`
- Format: comma-separated list of origins
- Safe default: if unset or empty, no origins are allowed (i.e. denied by default)

- Env var: `IMS_CORS_ALLOW_CREDENTIALS`
  - Optional: explicitly allow credentialed CORS requests from allowlisted origins (e.g. cookies/sessions)
  - Values: `true`/ `1`/ `yes`/ `on` (case-insensitive)
  - Safe default: if unset/empty/unrecognized, credentials are disallowed `False`

Enabling credentials increases the risk of misconfiguration and broadens the cross-origin attack surface, so only enable it if you intentionally use cookie/browser-credential auth from a different origin.

Example (local frontend at http://localhost:3000):

```bash
export IMS_CORS_ALLOW_ORIGINS="http://localhost:3000"
# Optional: only if you need credentialed CORS
export IMS_CORS_ALLOW_CREDENTIALS="true"
uvicorn backend.main:app --reload
```

## Authentication

Write endpoints (`POST /api/items`, `PATCH /api/items/{item_id}`, `DELETE /api/items/{item_id}`)
require an authenticated identity. Authentication is identity-based: each
user has their own username/password and a role (`operator`, `supervisor`,
or `admin`) stored in the `users` table, and authorization is derived from
that identity's role - not from a shared secret token (see CAP-49; this
replaces the CAP-46 shared env-var bearer tokens).

- POST/PATCH `/api/items`: any of `operator`, `supervisor`, `admin`
- DELETE `/api/items/{item_id}`: `admin` only
- Missing/invalid/expired/revoked credentials: `401 Unauthorized`
- Authenticated but insufficient role: `403 Forbidden`

### Bootstrapping the first admin

There is no hardcoded default admin account. On startup, if the `users`
table is empty, the app creates a single initial admin from two env vars -
if either is unset, bootstrap is skipped (and a warning is logged):

```bash
export IMS_ADMIN_BOOTSTRAP_USERNAME="admin"
export IMS_ADMIN_BOOTSTRAP_PASSWORD="change-me-immediately"
uvicorn backend.main:app --reload
```

This only ever runs while the `users`
table has zero rows, so it cannot be
used to reset or overwrite an existing admin - once at least one user
exists, provision further users directly via the database (there is
intentionally no user-management endpoint in this ticket's scope).

### Logging in
```bash
curl -s -X POST http://127.0.0.1:8000/api/auth/login \\
  -H "Content-Type: application/json" \\
  -d '{"username": "admin", "password": "change-me-immediately"}'
```

Response:

```json
{
  "access_token": "<jwt>",
  "token_type": "bearer",
  "role": "admin"
}
```

### Calling a protected endpoint

```bash
curl -s -X POST http://127.0.0.1:8000/api/items \\
  -H "Authorization: Bearer <jwt>" \\
  -H "Content-Type: application/json" \\
  -d '{"sku": "SKU-2001", "name": "Shipping Box", "category": "Packaging", "quantity": 40, "reorder_level": 10, "location": "Aisle 2", "notes": ""}'
```

### Logging out / revocation
Tokens are JWTs signed with a server-side secret and carry a unique `jti`
claim. `POST /api/auth/logout` (with the token to invalidate in the
`Authorization` header) records that `jti` in the `revoked_tokens` table;
every subsequent request checks that table, so a revoked token stops
working immediately without requiring any client redeploy or rotation of a
shared secret.

```bash
curl -s -X POST http://127.0.0.1:8000/api/auth/logout \
  -H "Authorization: Bearer <jwt>"
```

### Env vars

- `IMS_JWT_SECRET`: secret used to sign/verify JWTs. **Must be set to a
  strong, random value in production** - if unset, a fixed insecure
  development default is used (fine for local dev only; never rely on it
  outside a throwaway local environment).
- `IMS_JWT_TTL_SECONDS`: optional token lifetime in seconds. Defaults to
  28800 (8 hours) if unset.
- `IMS_ADMIN_BOOTSTRAP_USERNAME` / `IMS_ADMIN_BOOTSTRAP_PASSWORD`: optional,
  used only once (see "Bootstrapping the first admin" above) to create the
  first admin user when the `users` table is empty.

Password hashes are stored using PBKDF2-HMAC-SHA256 with a random per-user
salt (stdlib `hashlib`, no extra dependency); passwords themselves are
never stored or logged.

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

CI runs `pytest -q` directly (not `python -m pytest`), so `pytest.ini` pins
`pythonpath = .` and `testpaths = tests` — otherwise `tests/conftest.py`'s
`import backend.database` fails to resolve under a bare `pytest` invocation,
and discovery could pick up stray test-like files outside `tests/`.

## Project Structure

```text
backend/   FastAPI application and SQLite access
frontend/  Static HTML/CSS/JS user interface
doc/       High-level, low-level, architecture, and Confluence docs
tests/     Automated tests
```
