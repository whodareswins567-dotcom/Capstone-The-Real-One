# High-Level Design

## Purpose

The inventory management system tracks stock items, quantities, reorder levels, categories, and storage locations.

## Users

- Inventory operator: adds, updates, searches, and removes inventory records.
- Supervisor: reviews low-stock items and plans replenishment.
- Administrator: manages inventory configuration and operational oversight.

## Authentication & Authorization

Write endpoints (create/update/delete) are protected with minimal Bearer token authentication.

Required header:

- `Authorization: Bearer <token>`

Tokens are configured via environment variables:

 - `IMS_OPERATOR_TOKEN`
 - `IMS_SUPERVISOR_TOKEN`
 - `IMS_ADMIN_TOKEN`

## Role Permission Matrix

| Endpoint | Operator | Supervisor | Admin |
|---|---|----|---|
| POST /api/items | ✅ | ✅ | ✅ |
| PATCH /api/items/{id} | ✅ | ✅ | ✅ |
| DELETE /api/items/{id} | ✔ – (043) | ✔ – (043) | ✅ | 
