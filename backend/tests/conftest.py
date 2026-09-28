import pytest
from fastapi.testclient import TestClient

from backend import database as db
from backend.main import app


@pytest.fixture()
def client(tmp_path, monkeypatch):
    """
    Returns a TestClient backed by an isolated, unseeded temporary SQLite database.

    DB_PATH is read at call time inside get_connection(), so monkeypatching
    it directly here takes effect immediately -- no env var + module reload
    dance needed, which avoids import-order flakiness. SEED_ON_STARTUP is
    disabled so tests don't depend on the dev sample data.
    """
    db_path = tmp_path / "inventory_test.db"
    monkeypatch.setattr(db, "DB_PATH", db_path)
    monkeypatch.setattr(db, "SEED_ON_STARTUP", False)

    with TestClient(app) as test_client:
        yield test_client
