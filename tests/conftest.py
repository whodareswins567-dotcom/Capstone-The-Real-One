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
    monkeypatch.setattr(db, "DB_PATH", db_path)

    # paranoia: ensure we don't touch the repo-checked-in DB.
    assert "test-inventory.db" in str(db.DB_PATH)

    db.init_db()
    db.seed_db()

    main = importlib.import_module("backend.main")
    with TestClient(main.app) as test_client:
        yield test_client
