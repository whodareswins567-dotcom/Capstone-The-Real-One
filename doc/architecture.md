# Architecture

## Overview

The system uses a simple three-part architecture:

```text
Browser UI -> FastAPI REST API -> SQLite Database
```

## Component Responsibilities

### Browser UI

The browser UI renders the inventory table, handles the add/edit form, and calls backend REST endpoints.

### FastAPI API

The FastAPI backend owns validation, database access, and API responses. It also serves the static frontend files.

### SQLite Database

SQLite stores inventory records in a local database file. This keeps the project easy to run during early development.

### Identity / Auth

Individual users authenticate via `POST /api/auth/login` (username +
password checked against the `users` table) and receive a signed JWT
carrying their role and a unique `jti`. Write endpoints resolve the
authenticated identity from that JWT and authorize based on its role
(operator/supervisor/admin), rather than a shared token. `POST
/api/auth/logout` records the token's `jti` in `revoked_tokens`, which is
checked on every authenticated request, enabling revocation without a
client redeploy.

## Data Flow

1. User opens `/`.
2. FastAPI serves `frontend/index.html`.
3. JavaScript calls `/api/items`.
4. FastAPI queries SQLite and returns JSON.
5. JavaScript renders the inventory table.
6. User creates, edits, or deletes items through REST calls.
7. Mutating calls (create/update/delete) require a bearer JWT obtained from `/api/auth/login`; the API resolves the identity, checks revocation, and enforces role-based authorization before touching SQLite.
