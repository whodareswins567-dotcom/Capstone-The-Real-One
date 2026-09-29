import pytest



@pytest.fixture
def auth_tokens(monkeypatch):
    """Configure env tokens for tests.

    Tests should never depend on real secrets; we set explicit
    tokens here so auth behavior is deterministic.
    """
    monkeypatch.setenv("IMS_OPERATOR_TOKEN", "operator-token")
    monkeypatch.setenv("IMS_SUPERVISOR_TOKEN", "supervisor-token")
    monkeypatch.setenv("IMS_ADMIN_TOKEN", "admin-token")
    return {
        "operator": "operator-token",
        "supervisor": "supervisor-token",
        "admin": "admin-token",
    }



@pytest.fixture
def headers(auth_tokens):
    return {
        "operator": {"Authorization": f"Bearer {auth_tokens['operator']}"},
        "supervisor": {"Authorization": f"Bearer {auth_tokens['supervisor']}"},
        "admin": {"Authorization": f"Bearer {auth_tokens['admin']}"},
    }



@pytest.fixture
def client(tmp_path, auth_tokens):
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
