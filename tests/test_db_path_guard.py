import pytest


def test_get_db_path_resolves_to_env_override(tmp_path, monkeypatch):
    db_path = tmp_path / "guard-test.db"
    monkeypatch.setenv("INVENTORY_DB_PATH", str(db_path))

    from backend import database as db

    assert db.get_db_path() == db_path


def test_get_db_path_raises_without_env_override_under_pytest(monkeypatch):
    monkeypatch.delenv("INVENTORY_DB_PATH", raising=False)

    from backend import database as db

    with pytest.raises(RuntimeError):
        db.get_db_path()
