def test_create_item_success(create_item):
    response = create_item("sku-crud-1")
    assert response.status_code == 201
    body = response.json()
    assert body["sku"] == "sku-crud-1"
    assert "id" in body


def test_list_items_returns_created_item(client, create_item):
    create_item("sku-crud-2", name="Widget", category="Tools")
    response = client.get("/api/items")
    assert response.status_code == 200
    items = response.json()
    assert any(item["sku"] == "sku-crud-2" for item in items)


def test_update_item_success(client, create_item):
    create = create_item("sku-crud-3")
    item_id = create.json()["id"]
    response = client.patch(f"/api/items/{item_id}", json={"name": "New Name"})
    assert response.status_code == 200
    assert response.json()["name"] == "New Name"


def test_delete_item_success(client, create_item):
    create = create_item("sku-crud-4")
    item_id = create.json()["id"]
    response = client.delete(f"/api/items/{item_id}")
    assert response.status_code == 204

    list_response = client.get("/api/items")
    assert list_response.status_code == 200
    assert not any(item["id"] == item_id for item in list_response.json())
