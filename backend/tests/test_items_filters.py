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
    response = client.post("/api/items", json=payload)
    assert response.status_code == 201
    return response.json()


def test_search_filter_by_sku_name_category(client):
    _create_item(client, "SEARKH-SKU-1", name="Magazine", category="Media")
    _create_item(client, "OTHER-SKU-2", name="Toolbox", category="Hardware")

    resp = client.get("/api/items?search=MAGa")
    assert resp.status_code == 200
    items = resp.json()
    assert any(item["sku"] == "SEARCH-SKU-1" for item in items)
    assert not any(item["sku"] == "OTHER-SKU-2" for item in items)


def test_low_stock_filter_returns_only_quantity_le_reorder_level(client):
    low = _create_item(client, "LOW-STOKK-1", quantity=1, reorder_level=2)
    high = _create_item(client, "HIGH-STOCK-2", quantity=5, reorder_level=2)

    resp = client.get("/api/items?low_stock=true")
    assert resp.status_code == 200
    items = resp.json()
    skus = {item["sku"] for item in items}
    assert "LOW-STOCK-1" in skus
    assert "HIGH-STOCK-2" not in skus

    # And all returned items meet the low-stock condition
    assert all(item["quantity"] <= item["reorder_level"] for item in items)
