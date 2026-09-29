import pytest



@pytest.fixture
def db_path(tmp_path):
    """Path to an isolated per-test SQLite db file (created by the app's
    lifespan on first use via the `client` fixture).
    """
    return tmp_path / "test-inventory.db"



@pytest.fixture
def client(db_path):
    """Create a test client backed by an isolated temp SQLite database.

    db_path is passed directly to create_app(), which pins it on
    app.state and threads it through init_db()/seed_db()/get_app_db_path()
    - so isolation is guaranteed by dependency injection, not by an env var.
    backend.main is imported here rather than at module scope so no backend
    import-time side effects can run before the fixture.
    """
    from fastapi.testclient import TestClient

    from backend.main import create_app

    app = create_app(db_path=db_path)
    assert app.state.db_path == db_path

    with TestClient(app) as test_client:
        yield test_client



def _insert_user(db_path, username: str, password: str, role) -> None:
    """Insert a user directly into the test's isolated db.

    This bypasses the HTTP API (there is intentionally no user-creation
    endpoint yet - see CAP-49) but exercises the same password hashing
    (backend.auth.hash_password) used by admin bootstrap, so a subsequent
    POST /api/auth/login with this username/password behaves exactly as it
    would for a real user.
    """
    from backend.auth import hash_password
    from backend.database import get_connection

    with get_connection(db_path) as connection:
        connection.execute(
            "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
            (username, hash_password(password), role.value),
        )



@pytest.fixture
def auth_tokens(client, db_path):
    """Create one user per role directly in the test db, then log in via
    POST /api/auth/login to obtain real JWTs.

    Replaces the legacy CAP-46 env-token monkeypatching now that auth is
    identity-based (CAP-49): each role's "token" here is a genuine signed
    JWT issued for a distinct user identity, not a shared secret from the
    environment.
    """
    from backend.auth import Role

    credentials = {
        "operator": ("operator-user", "operator-pass-1"),
        "supervisor": ("supervisor-user", "supervisor-pass-1"),
        "admin": ("admin-user", "admin-pass-1"),
    }
    roles = {
        "operator": Role.OPERATOR,
        "supervisor": Role.SUPERVISOR,
        "admin": Role.ADMIN,
    }

    tokens = {}
    for role_name, (username, password) in credentials.items():
        _insert_user(db_path, username, password, roles[role_name])
        resp = client.post(
            "/api/auth/login",
            json={"username": username, "password": password},
        )
        assert resp.status_code == 200, resp.text
        tokens[role_name] = resp.json()["access_token"]

    return tokens



@pytest.fixture
def headers(auth_tokens):
    return {
        "operator": {"Authorization": f"Bearer {auth_tokens['operator']}"},
        "supervisor": {"Authorization": f"Bearer {auth_tokens['supervisor']}"},
        "admin": {"Authorization": f"Bearer {auth_tokens['admin']}"},
    }
