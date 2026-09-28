import importlib


import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client(tmp_path, monkeypatch):
    """Create a test client that uses a temporary SQLite database.

    Important: the app lifespan calls init_db()/seed_db(), so
    we must redirect DB_PATH BEFORE constructing TestClient.
    """
    db_path = tmp_path / "test-inventory.db"

    db = importlib.import_module("backend.database")
    default_db_path = db.BASE_DIR / "inventory.db"

    # Redirect DB_PATH BEFORE any app code creates connections.
    monkeypatch.setattr(db, "DB_PATH", db_path)

    # Guard: tests must not touch the repo default DB.
    assert db.DB_PATH != default_db_path
    assert "test-inventory.db" in str(db.DB_PATH)

    db.init_db()
    db.seed_db()

    main = importlib.import_module("backend.main")
    with TestClient(main.app) as test_client:
        yield test_client
