import os
import importlib

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client(tmp_path, monkeypatch):
    """Create a test client that uses a temporary SQLite database.

    Important: the app lifespan calls init_db()/seed_db(), so
    we must set INVENTORY_DB_PATH BEFORE constructing TestClient.
    """
    db_path = tmp_path / "test-inventory.db"
    monkeypatch.setenv("INVENTORY_DB_PATH", str(db_path))

    # Instantiate/reload modules after env var is set.
    db = importlib.import_module("backend.database")
    importlib.reload(db)

    # paranoia: ensure we don't touch a repo DB.
    assert "test-inventory.db" in str(db.DB_PATH)

    db.init_db()
    db.seed_db()

    main = importlib.import_module("backend.main")
    importlib.reload(main)

    with TestClient(main.app) as test_client:
        yield test_client
