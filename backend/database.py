from pathlib import Path
import logging
import os
import sqlite3


BASE_DIR = Path(__file__).resolve().parent
DEFAULT_DB_PATH = BASE_DIR / "inventory.db"

logger = logging.getLogger(__name__)


def get_db_path() -> Path:
    """Resolve the SQLite DB path from INVENTORY_DB_PATH, falling back to
    backend/inventory.db. Callers that need isolation should pass db_path
    explicitly to get_connection()/init_db()/seed_db() instead of relying
    on this env var.
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
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS revoked_tokens (
                jti TEXT PRIMARY KEY,
                expires_at INTEGER,
                revoked_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
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


def bootstrap_admin_if_empty(db_path: Path | str | None = None) -> None:
    """Create the first admin user if the users table is empty.

    This only runs an insert when both IMS_ADMIN_BOOTSTRAP_USERNAME and
    IMS_ADMIN_BOOTSTRAP_PASSWORD are set - there is intentionally no
    hardcoded default admin/password. If the users table already has at
    least one row, this is a no-op (bootstrap only ever creates the *first*
    admin identity).
    """
    # Imported locally (not at module scope) to avoid a circular import:
    # backend.auth imports get_connection from this module.
    from .auth import Role, hash_password

    with get_connection(db_path) as connection:
        existing = connection.execute("SELECT COUNT(*) AS n FROM users").fetchone()
        if existing["n"] > 0:
            return

        username = os.environ.get("IMS_ADMIN_BOOTSTRAP_USERNAME")
        password = os.environ.get("IMS_ADMIN_BOOTSTRAP_PASSWORD")
        if not username or not password:
            logger.warning(
                "users table is empty and IMS_ADMIN_BOOTSTRAP_USERNAME/"
                "IMS_ADMIN_BOOTSTRAP_PASSWORD are not both set - skipping "
                "initial admin bootstrap. Set both env vars and restart to "
                "create the first admin identity."
            )
            return

        connection.execute(
            "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
            (username, hash_password(password), Role.ADMIN.value),
        )
        logger.info("Bootstrapped initial admin user '%s'", username)
