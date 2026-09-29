# API Reference

## Authentication

```http
POST /api/auth/login
Content-Type: application/json
```

```json
{
  "username": "admin",
  "password": "change-me-immediately"
}
```

Response:

```json
{
  "access_token": "<jwt>",
  "token_type": "bearer",
  "role": "admin"
}
```

```http
POST /api/auth/logout
Authorization: Bearer <jwt>
```

Revokes the token used to authenticate the request. Returns `204 No Content`.

Protected write endpoints (`POST /api/items`, `PATCH /api/items/{item_id}`,
`DELETE /api/items/{item_id}`) require `Authorization: Bearer <jwt>` from a
login response. See README.md "Authentication" for the full role matrix and
bootstrap instructions.

## Health

```http
GET /api/health
```

Response:

```json
{
  "status": "ok"
}
```

## List Items

```http
GET /api/items?search=tape&low_stock=true
```

Query parameters:

- `search`: optional text search across SKU, name, and category.
- `low_stock`: optional boolean.

## Create Item

```http
POST /api/items
Content-Type: application/json
```

```json
{
  "sku": "SKU-2001",
  "name": "Shipping Box",
  "category": "Packaging",
  "quantity": 40,
  "reorder_level": 10,
  "location": "Aisle 2",
  "notes": "Medium size"
}
```

## Update Item

```http
PATCH /api/items/1
Content-Type: application/json
```

```json
{
  "quantity": 35
}
```

## Delete Item

```http
DELETE /api/items/1
```

Returns `204 No Content` when successful.
