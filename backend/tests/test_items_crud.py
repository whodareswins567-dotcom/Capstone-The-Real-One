def _create_item(client, sku: str, **kwargs):
    payload = {
        "sku": sku,
        "name": kwargs.get("name", "Test Item"),
        "category": kwargs.get("category", "Test"),
        "quantity": kwargs.get("quantity", 10),
        "reorder_level": kwargs.get("reorder_level", 2),
        "location": kwargs.get("location", "A1"),
        "notes": kwargs.get("notes", ""),
    }
    return client.post("/api/items", json=payload)


def test_create_item_success(client):
    response = _create_item(client, "sku-crud-1")
    assert response.status_code == 201
    body = response.json()
    assert body["sku"] == "sku-crud-1"
    assert "id" in body


def test_list_items_returns_created_item(client):
    _create_item(client, "sku-crud-2", name="Widget", category="Tools")
    response = client.get("/api/items")
    assert response.status_code == 200
    items = response.json()
    assert any(item["sku"] == "sku-crud-2" for item in items)


def test_update_item_success(client):
    create = _create_item(client, "sku-crud-3")
    item_id = create.json()["id"]
    response = client.patch(f"/api/items/{item_id}", json={"name": "New Name"})
    assert response.status_code == 200
    assert response.json()["name"] == "New Name"



def test_delete_item_success(client):
    create = _create_item(client, "sku-crud-4")
    item_id = create.json()["id"]
    response = client.delete(f"/api/items/{item_id}")
    assert response.status_code == 204
