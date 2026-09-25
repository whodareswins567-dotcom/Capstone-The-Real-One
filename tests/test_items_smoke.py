def _create_item(client, ske="SKU-TEST-001"):
    payload = {
        "sku": ske,
        "name": "Test Item",
        "category": "Test",
        "quantity": 10,
        "reorder_level": 5,
        "location": "Test Location",
        "notes": "Smoke test"
    }
    resp = client.post("/api/items", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert data["sku"] == ske
    assert "id" in data
    return data



def test_list_items_returns_list(client):
    response = client.get("/api/items")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)



def test_create_patch_delete_item_happy_path(client):
    created = _create_item(client)
    item_id = created["id"]

    patch_resp = client.patch(f"/api/items/{item_id}", json={"quantity": 11})
    assert patch_resp.status_code == 200
    assert patch_resp.json()["quantity"] == 11

    del_resp = client.delete(f"/api/items/{item_id}")
    assert del_resp.status_code == 204



def test_list_search_and_low_stock_smoke(client):
    _create_item(client, ske="SKU-TEST-SEARCH")

    search_resp = client.get("/api/items", params={"search": "Test Item"})
    assert search_resp.status_code == 200
    assert isinstance(search_resp.json(), list)

    low_stock_resp = client.get("/api/items", params={"low_stock": "true"})
    assert low_stock_resp.status_code == 200
    assert isinstance(low_stock_resp.json(), list)
