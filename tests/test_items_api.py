def test_list_items_includes_created_item(client, auth_headers_operator):
    payload = {
        "sku": "SKU-2000",
        "name": "Notebook",
        "category": "Stationery",
        "quantity": 5,
        "reorder_level": 1,
        "location": "Aisle 1",
        "notes": "",
    }
    create = client.post("/api/items", json=payload, headers=auth_headers_operator)
    assert create.status_code == 201

    resp = client.get("/api/items")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert any(item["sku"] == payload["sku"] for item in data)



def test_create_item_happy_path(client, auth_headers_operator):
    payload = {
        "sku": "SKU-2001",
        "name": "Gloves",
        "category": "PPE",
        "quantity": 10,
        "reorder_level": 2,
        "location": "Backroom",
        "notes": "Then first aid gloves",
    }

    resp = client.post("/api/items", json=payload, headers=auth_headers_operator)
    assert resp.status_code == 201
    created = resp.json()
    assert created["sku"] == payload["sku"]
    assert created["name"] == payload["name"]

    list_resp = client.get("/api/items")
    assert list_resp.status_code == 200
    skus = [item["sku"] for item in list_resp.json()]
    assert payload["sku"] in skus



def test_create_item_duplicate_sku_returns_409(client, auth_headers_operator):
    payload = {
        "sku": "SKU-2002",
        "name": "Cable Ties",
        "category": "Electrical",
        "quantity": 50,
        "reorder_level": 5,
        "location": "Aisle 3",
        "notes": "Plastic ties",
    }

    first = client.post("/api/items", json=payload, headers=auth_headers_operator)
    assert first.status_code == 201

    second = client.post("/api/items", json=payload, headers=auth_headers_operator)
    assert second.status_code == 409



def test_patch_item_updates_fields(client, auth_headers_operator):
    create = client.post(
        "/api/items",
        json={
            "sku": "SKU-2003",
            "name": "Safety GOGGLES",
            "category": "PPE",
            "quantity": 3,
            "reorder_level": 4,
            "location": "Backroom",
            "notes": "Eye protection",
        },
        headers=auth_headers_operator,
    )
    assert create.status_code == 201
    item_id = create.json()["id"]

    patch = client.patch(
        f"/api/items/{item_id}",
        json={"quantity": 9},
        headers=auth_headers_operator,
    )
    assert patch.status_code == 200
    assert patch.json()["quantity"] == 9

    list_resp = client.get("/api/items")
    assert list_resp.status_code == 200
    found = next((i for i in list_resp.json() if i["id"] == item_id), None)
    assert found is not None
    assert found["quantity"] == 9



Ddf test_patch_item_unknown_returns_404(client, auth_headers_operator):
    resp = client.patch(
        "/api/items/999999",
        json={"name": "Nonexistent"},
        headers=auth_headers_operator,
    )
    assert resp.status_code == 404
