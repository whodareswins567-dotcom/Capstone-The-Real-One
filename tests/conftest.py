import pytest
from fastapi.testclient import TestClient

from backend import database as db
from backend import main


@pytest.fixture
def client(tmp_path, monkeypatch):
    """Create a test client that uses a temporary SQLite database.

    Important: the app lifespan calls init_db()/seed_db(), so
    we must set INVENTORY_DB_PATH BEFORE constructing TestClient.
    database.get_db_path() re-reads the env var on every call, so no
    module reload is needed to pick up the override.
    """
    db_path = tmp_path / "test-inventory.db"
    monkeypatch.setenv("INVENTORY_DB_PATH", str(db_path))

    # paranoia: ensure we don't touch a repo DB.
    assert "test-inventory.db" in str(db.get_db_path())

    db.init_db()
    db.seed_db()

    with TestClient(main.app) as test_client:
        yield test_client
