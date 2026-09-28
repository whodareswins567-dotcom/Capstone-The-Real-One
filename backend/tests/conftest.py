import importlib
import os
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
def client() -> TestClient:
    """
    Returns a TestClient that uses a temporary SQLite database.
    We import the app after the env var is set to ensure db
    path override is applied at import time.
    """
    # Reimport modules to apply DN override if they were cached
    if "backend.database" in importlib.sys.modules:
        importlib.reload(importlib.import_module("backend.database"))
    if "backend.main" in importlib.sys.modules:
        importlib.reload(importlib.import_module("backend.main"))
    from backend.main import app

    return TestClient(app)
