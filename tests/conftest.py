import pytest


@pytest.fixture
def client(tmp_path):
    """Create a test client backed by an isolated temp SQLite database.

    db_path is passed directly to create_app(), which pins it on
    app.state and threads it through init_db()/seed_db()/get_app_db_path()
    - so isolation is guaranteed by dependency injection, not by an env var.
    backend.main is imported here rather than at module scope so no backend
    import-time side effects can run before the fixture.
    """
    from fastapi.testclient import TestClient

    from backend.main import create_app

    db_path = tmp_path / "test-inventory.db"
    app = create_app(db_path=db_path)
    assert app.state.db_path == db_path

    with TestClient(app) as test_client:
        yield test_client
