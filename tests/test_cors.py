import pytest



def _preflight(client, *, origin: str):
    return client.options(
        "/api/health",
        headers={
            "Origin": origin,
            "Access-Control-Request-Method": "GET",
        },
    )


def test_cors_allows_configured_origin(monkeypatch, tmp_path):
    monkeypatch.setenv("IMS_CORS_ALLOW_ORIGINS", "https://allowed.example")

    from fastapi.testclient import TestClient
    from backend.main import create_app

    app = create_app(db_path=tmp_path / "db.db")
    with TestClient(app) as client:
        res = _preflight(client, origin="https://allowed.example")
        assert res.status_code in (200, 204)
        assert res.headers.get("access-control-allow-origin") == "https://allowed.example"


def test_cors_blocks_disallowed_origin(monkeypatch, tmp_path):
    monkeypatch.setenv("IMS_CORS_ALLOW_ORIGINS", "https://allowed.example")

    from fastapi.testclient import TestClient
    from backend.main import create_app

    app = create_app(db_path=tmp_path / "db.db")
    with TestClient(app) as client:
        res = _preflight(client, origin="https://evil.example")
        # Starlette's CORSMiddleware returns 400 for a disallowed-origin preflight.
        assert res.status_code in (200, 204, 400)
        assert res.headers.get("access-control-allow-origin") is None


def test_cors_denies_by_default_when_unset(monkeypatch, tmp_path):
    monkeypatch.delenv("IMS_CORS_ALLOW_ORIGINS", raising=False)

    from fastapi.testclient import TestClient
    from backend.main import create_app

    app = create_app(db_path=tmp_path / "db.db")
    with TestClient(app) as client:
        res = _preflight(client, origin="https://any.example")
        # Starlette's CORSMiddleware returns 400 for a disallowed-origin preflight.
        assert res.status_code in (200, 204, 400)
        assert res.headers.get("access-control-allow-origin") is None
