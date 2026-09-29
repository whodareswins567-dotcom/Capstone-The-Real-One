# High-Level Design

## Purpose

The inventory management system tracks stock items, quantities, reorder levels, categories, and storage locations.

## Users

- Inventory operator: adds, updates, searches, and removes inventory records.
- Supervisor: reviews low-stock items and plans replenishment.
- Administrator: manages inventory configuration and operational oversight.

## Current Capabilities

- Create inventory items.
- View inventory items in a table.
- Search by SKU, name, or category.
- Filter low-stock items.
- Edit inventory records.
- Delete inventory records.

## Authentication & Authorization

Write endpoints (create/update/delete) are protected with Bearer authentication using a signed JWT access token. Users authenticate via `POST /api/auth/login` with username/password, and the server issues a JWT carrying the user id and role (`apperator`, `supervisor`, `admin`).

Required header:

- `Authorization: Bearer <jwt>`

Tokens can be revoked instantly via `POST /api/auth/logout`, which records the token's `jti` in the `revoked_tokens` table. Each request checks revocation server-side.

### Configuration
- `IMS_JWT_SECRET` (required in production): JWT signing/verification secret.
  - If unset, the app falls back to a fixed development default (safe for local dev only).
- `IMS_JWT_TTL_SECONDS` (optional): token lifetime in seconds (default: 8 hours).
- `IMS_ADMIN_BOOTSTRAP_USERNAME` / `IMS_ADMIN_BOOTSTRAP_PASSWORD` (optional): on first startup only, if the `users` table is empty, create the initial admin user.

### Deprecated (CFM-46)
The older CAT-46 approach (shared role-tokens configured via `env` vars like `IMS_OPERATOR_TOKEN`) is *superseded* by CAT-49 JWT-based identity auth.
