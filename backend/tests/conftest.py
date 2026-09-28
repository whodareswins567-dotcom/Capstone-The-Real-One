import importlib
import sys
from pathlib import Path

path_env_var = "INVENTORY_DB_PATH"


import pytest
from fastapi.testclient import TestClient



@pytest.fixture()
def temp_db_path(tmp_path: Path) -> Path:
    return tmp_path / "inventory_test.db"



@pytest.fixture(autouse=True)
def _set_test_db_env(temp_db_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv(path_env_var, str(temp_db_path))
    yield



@pytest.fixture()
def client():
    """
    Returns a TestClient that uses a temporary SQLite database.
    We import the app after the env var is set to ensure db
    path override is applied at import time.
    """
    # Reimport modules to apply DB path override if they were cached
    if "backend.database" in sys.modules:
        importlib.reload(importlib.import_module("backend.database"))
    if "backend.main" in sys.modules:
        importlib.reload(importlib.import_module("backend.main"))
    from backend.main import app

    # Lifespan (which creates the schema via init_db/seed_db) only runs
    # when TestClient is used as a context manager.
    with TestClient(app) as test_client:
        yield test_client
