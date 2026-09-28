import pytest
from fastapi.testclient import TestClient

from backend.main import create_app


@pytest.fixture
def client(tmp_path):
    """Create a test client backed by an isolated temp SQLite database.

    db_path is passed directly to create_app(), which pins it on
    app.state and threads it through init_db()/seed_db()/get_db_connection()
    - so isolation is guaranteed by dependency injection, not by import
    order or an env var.
    """
    db_path = tmp_path / "test-inventory.db"
    app = create_app(db_path=db_path)

    with TestClient(app) as test_client:
        yield test_client
