import sqlite3


def test_create_item_is_committed_before_response_is_returned(tmp_path):
    """Guards against committing in a yield-dependency teardown, which FastAPI
    runs only after the response has been produced."""
    from fastapi.testclient import TestClient

    from backend.main import create_app

    db_path = tmp_path / "commit-test.db"
    app = create_app(db_path=db_path)
    seen_at_response_time = []

    @app.middleware("http")
    async def check_committed(request, call_next):
        response = await call_next(request)
        if request.method == "POST":
            with sqlite3.connect(db_path) as connection:
                row = connection.execute(
                    "SELECT 1 FROM inventory_items WHERE sku = ?", ("SKU-3000",)
                ).fetchone()
            seen_at_response_time.append(row is not None)
        return response

    with TestClient(app) as client:
        resp = client.post(
            "/api/items",
            json={
                "sku": "SKU-3000",
                "name": "Commit Check",
                "category": "Misc",
                "quantity": 1,
                "reorder_level": 1,
                "location": "A1",
                "notes": "",
            },
            headers={"X-API-Key": "test-key", "X-User-Role": "inventory_operator"},
        )

    assert resp.status_code == 201
    assert seen_at_response_time == [True]
