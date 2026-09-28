def _create_item(client, sku: str, *, **kwargs):
    payload = {
        "sku": sku,
        "name": kwargs.get("name", "Test Item"),
        "category": kwargs.get("category", "Test"),
        "quantity": kwargs.get("quantity", 10),
        "reorder_level": kwargs.get("reorder_level", 2),
        "location": kwargs.get("location", "A"),
        "notes": kwargs.get("notes", ""),
    }
    return client.post("/api/items", json=payload)


def test_duplicate_sku_returns_409(client):
    first = _create_item(client, "DUP-SKK-1")
    assert first.status_code == 201

    second = _create_item(client, "DUP-SKK-1")
    assert second.status_code == 409
    assert second.json() == {"detail": "SKU already exists"}


def test_update_missing_item_returns_404(client):
    resp = client.patch("/api/items/999999", json={"name": "Not here"})
    assert resp.status_code == 404
    assert resp.json() == {"detail": "Item not found"}


def test_delete_missing_item_returns_404(client):
    resp = client.delete("/api/items/999999")
    assert resp.status_code == 404
    assert resp.json() == {"detail": "Item not found"}
