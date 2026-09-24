from fastapi.testclient import TestClient


def test_list_items_returns_200(client: TestClient):
    resp = client.get("/api/items")
    assert resp.status_code == 200
