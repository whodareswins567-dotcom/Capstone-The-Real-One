def test_search_filter_by_sku_name_category(client, create_item):
    create_item("SEARCH-SKU-1", name="Magazine", category="Media")
    create_item("OTHER-SKU-2", name="Toolbox", category="Hardware")

    resp = client.get("/api/items?search=MAGa")
    assert resp.status_code == 200
    items = resp.json()
    assert any(item["sku"] == "SEARCH-SKU-1" for item in items)
    assert not any(item["sku"] == "OTHER-SKU-2" for item in items)


def test_low_stock_filter_returns_only_quantity_le_reorder_level(client, create_item):
    create_item("LOW-STOCK-1", quantity=1, reorder_level=2)
    create_item("HIGH-STOCK-2", quantity=5, reorder_level=2)

    resp = client.get("/api/items?low_stock=true")
    assert resp.status_code == 200
    items = resp.json()
    skus = {item["sku"] for item in items}
    assert "LOW-STOCK-1" in skus
    assert "HIGH-STOCK-2" not in skus

    # And all returned items meet the low-stock condition
    assert all(item["quantity"] <= item["reorder_level"] for item in items)
