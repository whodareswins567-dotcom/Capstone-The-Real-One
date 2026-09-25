import os

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(autouse=True)
def _isolate_db_path(tmp_path):
    """Isolate each test to its own SQLite db file.

    Sets INVENTORY_DB_PATH env var added in backend.database.
    """
    db = tmp_path / "inventory_test.db"
    os.environ["INVENTORY_DB_PATH"] = str(db)
    yield
    os.environ.pop("INVENTORY_DB_PATH", None)


@pytest.fixture
def client():
    # Delayed import so env var is set before backend initializes DB path.
    from backend.main import app

    with TestClient(app) as client:
        yield client
