from pathlib import Path
import os
import sqlite3


BASE_DIR = Path(__file__).resolve().parent
DEFAULT_DB_PATH = BASE_DIR / "inventory.db"


def get_db_path() -> Path:
    """Resolve the SQLite DB path at call time (not import time), so
    tests can override INVENTORY_DB_PATH via monkeypatch without
    needing importlib.reload. Falls back to backend/inventory.db.
    """
    db_path = os.environ.get("INVENTORY_DB_PATH")
    if db_path is None:
        if "PYTEST_CURRENT_TEST" in os.environ:
            # PYTEST_CURRENT_TEST is set by pytest itself, only for the
            # duration of an actual test run - not by app/production code.
            raise RuntimeError(
                "INVENTORY_DB_PATH is not set while running under pytest; "
                "tests must set it before importing backend.database/backend.main "
                "to avoid touching the default repo DB."
            )
        return DEFAULT_DB_PATH
    return Path(db_path)


def get_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(get_db_path())
    connection.row_factory = sqlite3.Row
    return connection


def init_db() -> None:
    with get_connection() as connection:
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


def seed_db() -> None:
    sample_items = [
        ("SKU-1001", "Barcode Scanner", "Electronics", 8, 3, "Aisle 1", "Shared scanner pool"),
        ("SKU-1002", "Thermal Labels", "Stationery", 120, 50, "Aisle 4", "50mm x 25mm rolls"),
        ("SKU-1003", "Packing Tape", "Packaging", 22, 25, "Aisle 2", "Low stock example"),
    ]

    with get_connection() as connection:
        for item in sample_items:
            connection.execute(
                """
                INSERT OR IGNORE INTO inventory_items
                  (sku, name, category, quantity, reorder_level, location, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                item,
            )
