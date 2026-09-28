def test_get_db_path_resolves_to_env_override(tmp_path, monkeypatch):
    db_path = tmp_path / "guard-test.db"
    monkeypatch.setenv("INVENTORY_DB_PATH", str(db_path))

    from backend import database as db

    assert db.get_db_path() == db_path


def test_get_db_path_falls_back_to_default_without_env_override(monkeypatch):
    monkeypatch.delenv("INVENTORY_DB_PATH", raising=False)

    from backend import database as db

    assert db.get_db_path() == db.DEFAULT_DB_PATH


def test_get_connection_accepts_explicit_db_path_override(tmp_path, monkeypatch):
    """Explicit db_path bypasses INVENTORY_DB_PATH entirely - this is what
    backend.main.create_app()/tests/conftest.py rely on for isolation,
    instead of the old import-order convention."""
    monkeypatch.delenv("INVENTORY_DB_PATH", raising=False)
    db_path = tmp_path / "explicit-override.db"

    from backend import database as db

    db.init_db(db_path)
    assert db_path.exists()

    with db.get_connection(db_path) as connection:
        tables = connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
    assert any(row["name"] == "inventory_items" for row in tables)
