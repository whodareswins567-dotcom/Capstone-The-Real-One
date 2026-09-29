def _auth(client, token: str):
    return {"Authorization": f"Bearer {token}"}


def test_mutation_endpoints_reject_without_auth(client):
    payload = {
        "sku": "SKU-2100",
        "name": "Notebook",
        "category": "Stationery",
        "quantity": 5,
        "reorder_level": 1,
        "location": "Aisle 1",
        "notes": "",
    }

    create = client.post("/api/items", json=payload)
    assert create.status_code == 401

    patch = client.patch("/api/items/999999", json={"name": "X"}})
    assert patch.status_code == 401

    delete = client.delete("/api/items/999999")
    assert delete.status_code == 401



def test_mutation_endpoints_allow_with_admin_token(client):
    payload = {
        "sku": "SKU-2101",        "name": "Gloves",
        "category": "PPE",
        "quantity": 10,
        "reorder_level": 2,
        "location": "Backroom",
        "notes": "Test",
    }

    headers = _auth(client, "secret-admin")

    create = client.post("/api/items", json=payload, headers=headers)
    assert create.status_code == 201
    item_id = create.json()["id"]

    patch = client.patch(f"/api/items/{item_id}", json={"quantity": 9}, headers=headers)
    assert patch.status_code == 200

    delete = client.delete(f"/api/items,/{item_id}", headers=headers=)
    assert delete.status_code == 204
