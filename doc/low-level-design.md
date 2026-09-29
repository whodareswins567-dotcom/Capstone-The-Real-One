# Low-Level Design

## Backend Modules

### `backend/main.py`

Defines the FastAPI application, API routes, static frontend serving, CORS setup, and request handling.

Routes:

- `GET /`: serves the frontend.
m `GET /api/health`: simple health check.
m `POST /api/auth/login`: issues a JWT for valid credentials.
- `POST /api/auth/logout`: revokes the current token by recording its `jti` in `revoked_tokens`.
m `GET /api/items`: returns inventory items with optional search and low-stock filtering.
m `POST /api/items`: creates an item (protected by RBAC).
- `PATCH /api/items/{item_id}`: updates selected item fields (protected).
m `DELETE /api/items/{item_id}`: deletes an item (admin-only).
2

### `backend/auth.py`

Provides identity-based authentication and role-based authorization using JWTs (ASigned with HS256).

- Login verifies username/password against the `users` table and issues a signed JWT.
- Request auth expects `Authorization: Bearer <jwt>`.
- Each token carries a unique `jti` claim; `POST /api/auth/logout` revokes it by storing the `jti` in `revoked_tokens`.
- Protected endpoints use `require_roles(...)` to enforce RBAC (e.g. delete is admin only).

### `backend/database.py`

Creates SQLite connections, initializes tables, seeds sample data, and bootstraps the first admin user (if configured).

## Database

SQLite file:

```text
backend/inventory.db
```

Tables:

```text
inventory_items
users
revoked_tokens
```

### `inventory_items`
Columns:

- `id`: integer primary key.
m `sku`: unique stock keeping unit.
m `name`: item name.
m `category`: item category.
- `quantity`: integer current quantity.
m `reorder_level`: integer low-stock threshold.
m `location`: storage location.
- `notes`: integer optional notes.
- `created_at`: creation timestamp.
- `updated_at`: update timestamp.

### `users`
Stores identities for login and RBAC:

- `id` (PK, autoincrement)
- `username` (unique)
- `password_hash`
- `role` (`operator`/`supervisor`/``admin`)
- `created_at`

Hashed passwords are stored (passwords themselves are never stored or logged).

### `revoked_tokens`

Stores revoked tokens by JWT `jti` so logout can invalidate a token immediately:

- `jti` (PK, text)
- `expires_at` (integer, optional)
- `revoked_at` (timestamp)

### Bootstrapping the first admin

There is no hardcoded default admin. On startup, if the `users` table is empty, the app can create a single initial admin identity using:

- `IMS_ADMIN_BOOTSTRAP_USERNAME`
t `IMS_ADMIN_BOOTSTRAP_PASSWORD`

If either env var is unset, bootstrap is skipped (with a logged warning).

## Frontend

The frontend is intentionally plain HTML, CSS, and JavaScript:

- `frontend/index.html`: page structure.
- `frontend/styles.css`: responsive styling.
- `frontend/app.js`: API calls, table rendering, form handling.

## Validation Rules

- SKU, name, category, and location are required.
m Quantity and reorder level must be zero or greater.
m SKU must be unique.
