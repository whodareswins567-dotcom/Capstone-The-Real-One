def test_list_items_non_empty_after_seed(client):
    resp = client.get("/api/items")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_create_item_happy_path(client):
    payload = {
        "sku": "SKU-2001",
        "name": "Gloves",
        "category": "PPE",
        "quantity": 10,
        "reorder_level": 2,
        "location": "Backroom",
        "notes": "Then first aid gloves",
    }

    resp = client.post("/api/items", json=payload)
    assert resp.status_code == 201
    created = resp.json()
    assert created["sku"] == payload["sku"]
    assert created["name"] == payload["name"]

    list_resp = client.get("/api/items")
    assert list_resp.status_code == 200
    skus = [item["sku"] for item in list_resp.json()]
    assert payload["sku"] in skus



def test_create_item_duplicate_sku_returns_409(client):
    payload = {
        "sku": "SKU-2002",
        "name": "Cable Ties",
        "category": "Electrical",
        "quantity": 50,
        "reorder_level": 5,
        "location": "Aisle 3",
        "notes": "Plastic ties",
    }

    first = client.post("/api/items", json=payload)
    assert first.status_code == 201

    second = client.post("/api/items", json=payload)
    assert second.status_code == 409



def test_patch_item_updates_fields(client):
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
     )
    assert create.status_code == 201
    item_id = create.json()["id"]

    patch = client.patch(f"/api/items/{item_id}", json={"quantity": 9})
    assert patch.status_code == 200
    assert patch.json()["quantity"] == 9

    list_resp = client.get("/api/items")
    assert list_resp.status_code == 200
    found = [i for i in list_resp.json() if i["id"] == item_id][0]
    assert found["quantity"] == 9


def test_patch_item_unknown_returns_404(client):
    resp = client.patch("/api/items/999999", json={"name": "Nonexistent"})
    assert resp.status_code == 404



def test_patch_item_empty_payload_returns_400(client):
    create = client.post(
        "/api/items",
        json={
            "sku": "SKU-2004",
            "name": "Masking Tape",
            "category": "Packaging",
            "quantity": 1,
            "reorder_level": 1,
            "location": "Aisle 2",
            "notes": "",
        },
    )
    assert create.status_code == 201
    item_id = create.json()["id"]

    resp = client.patch(f"/api/items/{item_id}", json={})
    assert resp.status_code == 400


def test_delete_item_204_and_removed(client):
    create = client.post(
        "/api/items",
        json={
            "sku": "SKU-2005",
            "name": "Staples",
            "category": "Stationery",
            "quantity": 100,
            "reorder_level": 10,
            "location": "Aisle 4",
            "notes": "",
        },
     )
    assert create.status_code == 201
    item_id = create.json()["id"]

    delete_resp = client.delete(f"/api/items/{item_id}")
    assert delete_resp.status_code == 204

    list_resp = client.get("/api/items")
    assert list_resp.status_code == 200
    ids = [item["id"] for item in list_resp.json()]
    assert item_id not in ids



def test_delete_item_unknown_returns_404(client):
    resp = client.delete("/api/items/999999")
    assert resp.status_code == 404


def test_search_filters_results(client):
    client.post(
        "/api/items",
        json={
            "sku": "SKU-2006",
            "name": "Unique Name xyz123",
            "category": "Misc",
            "quantity": 1,
            "reorder_level": 1,
            "location": "A1",
            "notes": "",
        },
    )

    resp = client.get("/api/items", params={"search": "xyz123"})
    assert resp.status_code == 200
    results = resp.json()
    assert len(results) >= 1
    assert any("xyz123" in item["name"] for item in results)



def test_low_stock_filters_results(client):
    client.post(
        "/api/items",
        json={
            "sku": "SKU-2007",
            "name": "Low Stock Widget",
            "category": "Widgets",
            "quantity": 1,
            "reorder_level": 5,
            "location": "A2",
            "notes": "",
        },
    )

    resp = client.get("/api/items", params={"low_stock": "true"})
    assert resp.status_code == 200
    results = resp.json()
    assert len(results) >= 1
    assert all(item["quantity"] <= item["reorder_level"] for item in results)
