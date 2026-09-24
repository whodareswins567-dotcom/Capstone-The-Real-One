# Low-Level Design

## Backend Modules

### `backend/main.py`

Defines the FastAPI application, API routes, static frontend serving, CORS setup, and request handling.

Routes:

- `GET /`: serves the frontend.
- `GET /api/health`: simple health check.
- `GET /api/items`: returns inventory items with optional search and low-stock filtering.
- `POST /api/items`: creates an item.
- `PATCH /api/items/{item_id}`: updates selected item fields.
- `DELETE /api/items/{item_id}`: deletes an item.

### `backend/database.py`

Creates SQLite connections, initializes the database table, and seeds sample data.

### `backend/models.py`

Contains Pydantic models for API validation and response serialization.

## Database

SQLite file:

```text
backend/inventory.db
```

Table:

```text
inventory_items
```

Columns:

- `id`: integer primary key.
- `sku`: unique stock keeping unit.
- `name`: item name.
- `category`: item category.
- `quantity`: current quantity.
- `reorder_level`: threshold for low-stock status.
- `location`: storage location.
- `notes`: optional notes.
- `created_at`: creation timestamp.
- `updated_at`: update timestamp.

## Frontend

The frontend is intentionally plain HTML, CSS, and JavaScript:

- `frontend/index.html`: page structure.
- `frontend/styles.css`: responsive styling.
- `frontend/app.js`: API calls, table rendering, form handling.

## Validation Rules

- SKU, name, category, and location are required.
- Quantity and reorder level must be zero or greater.
- SKU must be unique.
