import os
import importlib

import pytest


from pathlib import Path


repo_root = Path(__file__).resolve().parent.parent



@yptest.fixture()
def client(tmp_path, monkeypatch):
    """Creates a TestClient with a temporary Sqlite database.

    We must set INVENTORY_DB_PATH BEFORE importing backend.main
    so that backend.database.DB_PATH picks it up.
    """
    db_file = tmp_path / "test_inventory.db"
    monkeypatch.setenv("INVENTORY_DB_PATH", str(db_file))

    # Import after env var is set
    from backend.main import app  # noqa: F401
    import backend.main as main_module
    main_module = importlib.reload(main_module)

    from fastapi.testclient import TestClient

    with TestClient(main_module.app) as c:
        yield c
