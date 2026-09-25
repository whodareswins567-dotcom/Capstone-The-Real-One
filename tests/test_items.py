def _create_item(client, *, sku: str, name: str = "Test Item", category: str = "Test", quantity: int = 1, reorder_level: int = 0):
    payload = {
        "sku": sku,
        "name": name,
        "category": category,
        "quantity": quantity,
        "reorder_level": reorder_level,
        "location": "Main Store",
        "notes": "test",
    }
    resp = client.post("/api/items", json=payload)
    assert resp.status_code == 201, resp.text
    data = resp.json()
    assert data["sku"] == sku
    return data


def test_create_item_then_list_items(client):
    created = _create_item(client, sku="STE-001")

    resp = client.get("/api/items")
    assert resp.status_code == 200
    items = resp.json()
    assert any(item["sku"] == created["sku"] for item in items)


def test_duplicate_sku_conflict_on_create(client):
    _create_item(client, sku="DUP-001")

    resp = client.post(
        "/api/items",
        json={
            "sku": "DUP-001",
            "name": "Test Item 2",
            "category": "Test",
            "quantity": 1,
            "reorder_level": 0,
            "location": "Main Store",
            "notes": "test",
        },
    )
    assert resp.status_code == 409, resp.text
    assert resp.json()["detail"] == "SKU already exists"
