from pathlib import Path
import os
import sqlite3


BASE_DIR = Path(__file__).resolve().parent
DEFAULT_DB_PATH = BASE_DIR / "inventory.db"


def get_db_path() -> Path:
    """Resolve the SQLite DB path from INVENTORY_DB_PATH, falling back to
    backend/inventory.db. Callers that need explicit isolation (e.g. tests,
    via backend.main.create_app()) should pass a db_path directly to
    get_connection()/init_db()/seed_db() instead of relying on this env var.
    """
    db_path = os.environ.get("INVENTORY_DB_PATH")
    return Path(db_path) if db_path else DEFAULT_DB_PATH


def get_connection(db_path: Path | str | None = None) -> sqlite3.Connection:
    connection = sqlite3.connect(db_path or get_db_path())
    connection.row_factory = sqlite3.Row
    return connection


def init_db(db_path: Path | str | None = None) -> None:
    with get_connection(db_path) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS inventory_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sku TEXT NOT NULL UNIQUE,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                quantity INTEGER NOT NULL DEFAULT 0,
                reorder_level INTEGER NOT NULL DEFAULT 0,
                location TEXT NOT NULL DEFAULT 'Main Store',
                notes TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        connection.execute(
            """
            CREATE TRIGGER IF NOT EXISTS set_inventory_updated_at
            AFTER UPDATE ON inventory_items
            FOR EACH ROW
            BEGIN
                UPDATE inventory_items
                SET updated_at = CURRENT_TIMESTAMP
                WHERE id = OLD.id;
            END;
            """
        )


def seed_db(db_path: Path | str | None = None) -> None:
    sample_items = [
        ("SKU-1001", "Barcode Scanner", "Electronics", 8, 3, "Aisle 1", "Shared scanner pool"),
        ("SKU-1002", "Thermal Labels", "Stationery", 120, 50, "Aisle 4", "50mm x 25mm rolls"),
        ("SKU-1003", "Packing Tape", "Packaging", 22, 25, "Aisle 2", "Low stock example"),
    ]

    with get_connection(db_path) as connection:
        for item in sample_items:
            connection.execute(
                """
                INSERT OR IGNORE INTO inventory_items
                  (sku, name, category, quantity, reorder_level, location, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                item,
            )
