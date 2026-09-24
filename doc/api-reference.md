# API Reference

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
