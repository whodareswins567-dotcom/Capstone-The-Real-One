from pathlib import Path
from typing import Iterator
import sqlite3
from contextlib import asynccontextmanager

from fastapi import APIRouter, Depends, FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .database import get_connection, init_db, seed_db
from .models import InventoryItem, InventoryItemCreate, InventoryItemUpdate


ROOT_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = ROOT_DIR / "frontend"

router = APIRouter()


def map_item(row: sqlite3.Row) -> InventoryItem:
    data = dict(row)
    data["low_stock"] = data["quantity"] <= data["reorder_level"]
    return InventoryItem(**data)


def get_db_connection(request: Request) -> Iterator[sqlite3.Connection]:
    with get_connection(request.app.state.db_path) as connection:
        yield connection


@router.get("/", include_in_schema=False)
def index() -> FileResponse:
    return FileResponse(FRONTEND_DIR / "index.html")


@router.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/api/items", response_model=list[InventoryItem])
def list_items(
    search: str | None = Query(default=None),
    low_stock: bool = Query(default=False),
    connection: sqlite3.Connection = Depends(get_db_connection),
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

    rows = connection.execute(sql, params).fetchall()
    return [map_item(row) for row in rows]


@router.post("/api/items", response_model=InventoryItem, status_code=201)
def create_item(
    payload: InventoryItemCreate,
    connection: sqlite3.Connection = Depends(get_db_connection),
) -> InventoryItem:
    try:
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


@router.patch("/api/items/{item_id}", response_model=InventoryItem)
def update_item(
    item_id: int,
    payload: InventoryItemUpdate,
    connection: sqlite3.Connection = Depends(get_db_connection),
) -> InventoryItem:
    fields = payload.model_dump(exclude_unset=True)
    if not fields:
        raise HTTPException(status_code=400, detail="No fields provided")

    assignments = ", ".join(f"{field} = ?" for field in fields)
    values = list(fields.values())
    values.append(item_id)

    try:
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


@router.delete("/api/items/{item_id}", status_code=204)
def delete_item(
    item_id: int,
    connection: sqlite3.Connection = Depends(get_db_connection),
) -> None:
    cursor = connection.execute("DELETE FROM inventory_items WHERE id = ?", (item_id,))
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Item not found")


def create_app(db_path: Path | str | None = None) -> FastAPI:
    """Build the FastAPI app, optionally pinned to an explicit db_path.

    db_path is stored on app.state and resolved by get_db_connection()/
    init_db()/seed_db() at request/startup time - not here - so passing
    None keeps the normal INVENTORY_DB_PATH/default lookup in
    backend.database.get_db_path(). Tests pass an explicit path instead,
    which bypasses that env var entirely and guarantees isolation without
    relying on import order.
    """

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        init_db(db_path)
        seed_db(db_path)
        yield

    app = FastAPI(
        title="Inventory Management System",
        description="Partially implemented inventory API with intentional gaps.",
        version="0.1.0",
        lifespan=lifespan,
    )
    app.state.db_path = db_path

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")
    app.include_router(router)

    return app


app = create_app()
