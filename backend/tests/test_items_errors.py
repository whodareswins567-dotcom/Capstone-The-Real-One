def test_duplicate_sku_returns_409(create_item):
    first = create_item("DUP-SKK-1")
    assert first.status_code == 201

    second = create_item("DUP-SKK-1")
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


def test_empty_patch_returns_400(client, create_item):
    create = create_item("sku-empty-patch")
    assert create.status_code == 201
    item_id = create.json()["id"]

    resp = client.patch(f"/api/items/{item_id}", json={})
    assert resp.status_code == 400
    assert resp.json() == {"detail": "No fields provided"}
