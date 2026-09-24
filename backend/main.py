from pathlib import Path
import sqlite3
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .database import get_connection, init_db, seed_db
from .models import InventoryItem, InventoryItemCreate, InventoryItemUpdate


ROOT_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = ROOT_DIR / "frontend"


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    seed_db()
    yield


app = FastAPI(
    title="Inventory Management System",
    description="Partially implemented inventory API with intentional gaps.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


def map_item(row: sqlite3.Row) -> InventoryItem:
    data = dict(row)
    data["low_stock"] = data["quantity"] <= data["reorder_level"]
    return InventoryItem(**data)


@app.get("/", include_in_schema=False)
def index() -> FileResponse:
    return FileResponse(FRONTEND_DIR / "index.html")


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/items", response_model=list[InventoryItem])
def list_items(
    search: str | None = Query(default=None),
    low_stock: bool = Query(default=False),
) -> list[InventoryItem]:
    sql = "SELECT * FROM inventory_items"
    params: list[object] = []
    clauses = []

    if search:
        clauses.append("(sku LIKE ? OR name LIKE ? OR category LIKE ?)")
        term = f"%{search}%"
        params.extend([term, term, term])

    if low_stock:
        clauses.append("quantity <= reorder_level")

    if clauses:
        sql += " WHERE " + " AND ".join(clauses)

    sql += " ORDER BY updated_at DESC, id DESC"

    with get_connection() as connection:
        rows = connection.execute(sql, params).fetchall()
        return [map_item(row) for row in rows]


@app.post("/api/items", response_model=InventoryItem, status_code=201)
def create_item(payload: InventoryItemCreate) -> InventoryItem:
    try:
        with get_connection() as connection:
            cursor = connection.execute(
                """
                INSERT INTO inventory_items
                    (sku, name, category, quantity, reorder_level, location, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    payload.sku,
                    payload.name,
                    payload.category,
                    payload.quantity,
                    payload.reorder_level,
                    payload.location,
                    payload.notes,
                ),
            )
            row = connection.execute(
                "SELECT * FROM inventory_items WHERE id = ?",
                (cursor.lastrowid,),
            ).fetchone()
    except sqlite3.IntegrityError as exc:
        raise HTTPException(status_code=409, detail="SKU already exists") from exc

    return map_item(row)


@app.patch("/api/items/{item_id}", response_model=InventoryItem)
def update_item(item_id: int, payload: InventoryItemUpdate) -> InventoryItem:
    fields = payload.model_dump(exclude_unset=True)
    if not fields:
        raise HTTPException(status_code=400, detail="No fields provided")

    assignments = ", ".join(f"{field} = ?" for field in fields)
    values = list(fields.values())
    values.append(item_id)

    try:
        with get_connection() as connection:
            cursor = connection.execute(
                f"UPDATE inventory_items SET {assignments} WHERE id = ?",
                values,
            )
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Item not found")

            row = connection.execute(
                "SELECT * FROM inventory_items WHERE id = ?",
                (item_id,),
            ).fetchone()
    except sqlite3.IntegrityError as exc:
        raise HTTPException(status_code=409, detail="SKU already exists") from exc

    return map_item(row)


@app.delete("/api/items/{item_id}", status_code=204)
def delete_item(item_id: int) -> None:
    with get_connection() as connection:
        cursor = connection.execute("DELETE FROM inventory_items WHERE id = ?", (item_id,))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Item not found")
