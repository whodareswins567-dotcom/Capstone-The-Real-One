def test_list_items_returns_list(client):
    resp = client.get("/api/items")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)


def test_create_item_then_list_contains_it(client):
    payload = {
        "sku": "TKS-TEST-001",
        "name": "Test Item",
        "category": "Tests",
        "quantity": 1,
        "reorder_level": 1,
        "location": "Test Aisle",
        "notes": "created by test",
    }

    create = client.post("/api/items", json=payload)
    assert create.status_code == 201
    created = create.json()
    assert created["sku"] == payload["sku"]

    list_resp = client.get("/api/items")
    assert list_resp.status_code == 200
    skus = {item["sku"] for item in list_resp.json()}
    assert payload["sku"] in skus
