import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="session")
def client(tmp_path_factory):
    """A TestClient with a temporary SQLite DB path.

    The backend uses `INVENTORY_DB_PATH` in `backend.database` to allow tests to avoid touching a developer local db file.
    """
    db_file = tmp_path_factory.temporary_dir() / "test-inventory.db"
    os.environ["INVENTORY_DB_PATH"] = str(db_file)

    # Import after setting env var so backend.database picks up the test path.
    from backend.main import app  # noqqa: F401

    return TestClient(app)
