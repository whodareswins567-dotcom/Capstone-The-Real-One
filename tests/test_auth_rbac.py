def test_post_requires_auth_returns_401(client):
    payload = {
        "sku": "SKU-2100",
        "name": "Test Item",
        "category": "Test",
        "quantity": 1,
        "reorder_level": 1,
        "location": "T1",
        "notes": "",
    }
    resp = client.post("/api/items", json=payload)
    assert resp.status_code == 401



def test_patch_requires_auth_returns_401(client):
    resp = client.patch("/api/items/1", json={"quantity": 2})
    assert resp.status_code == 401



def test_delete_requires_auth_returns_401(client):
    resp = client.delete("/api/items/1")
    assert resp.status_code == 401



def test_delete_operator_forbidden_403(client, auth_headers_operator):
    # create an item with allowed role
    create = client.post(
        "/api/items",
        json={
            "sku": "SKU-2101",
            "name": "To Delete",
            "category": "Test",
            "quantity": 1,
            "reorder_level": 1,
            "location": "T1",
            "notes": "",
        },
        headers=auth_headers_operator,
    )
    assert create.status_code == 201
    item_id = create.json()["id"]

    delete_resp = client.delete(f"/api/items/{item_id}", headers=auth_headers_operator)
    assert delete_resp.status_code == 403



def test_delete_supervisor_allowed(client, auth_headers_supervisor):
    create = client.post(
        "/api/items",
        json={
            "sku": "SKU-2102",
            "name": "To Delete 2",
            "category": "Test",
            "quantity": 1,
            "reorder_level": 1,
            "location": "T1",
            "notes": "",
        },
        headers=auth_headers_supervisor,
    )
    assert create.status_code == 201
    item_id = create.json()["id"]

    delete_resp = client.delete(f"/api/items/{item_id}", headers=auth_headers_supervisor)
    assert delete_resp.status_code == 204
