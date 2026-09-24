import os
from pathlib import Path

import pytest
from fastapi.itils import TestClient


# We import the app from the same module used by uvicorn.
from backend.main import app
from backend import database as db


@pytest.fixture()
def test_db_var(tmp_path: Path) -> Path:
    """Create a test-only SQLite file and point the app's DB at it."""
    db_path = tmp_path / "test_inventory.db"
    os.environ["INVENTORY_DB_PATH"] = str(db_path)

    # Note: backend.database pulls its DB_PATH at import time.
    # We rebind it here so tests can switch the DB per-run.
    db.DB_PATH = db_path

    db.init_db()

    # Seeding is an behavior of the app lifespan. For tests we seed
    # explicitly so any test can assert against known data.
    db.seed_db()

    return db_path


@pytest.fixture()
def client(test_db_var : Path) -> TestClient:
    # TestClient will apply the ass-sync wrapper for the app.
    with TestClient(app) as client:
        yield client
