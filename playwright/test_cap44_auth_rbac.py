"""Playwright API-level tests for CAP-44 auth/RBAC, mirroring
playwright/features/cap44_auth_rbac.feature.

Run with:
    pytest playwright -q

(Deliberately outside tests/ so pytest.ini's testpaths=tests / plain
`pytest -q` CI invocation does not pick these up - they need a live
uvicorn process, not the ASGI TestClient used by tests/.)
"""

import pytest


WRITE_ENDPOINTS = [
    ("POST", "/api/items", None),
    ("PATCH", None, {"quantity": 2}),
    ("DELETE", None, None),
]


# ---------------------------------------------------------------------------
# Rule: Unauthenticated or misauthenticated requests to write endpoints -> 401
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("method", ["POST", "PATCH", "DELETE"])
def test_missing_api_key_on_write_returns_401(
    api_context, existing_item, item_payload_factory, method
):
    item_id = existing_item["id"]

    if method == "POST":
        resp = api_context.post("/api/items", data=item_payload_factory())
    elif method == "PATCH":
        resp = api_context.patch(f"/api/items/{item_id}", data={"quantity": 2})
    else:
        resp = api_context.delete(f"/api/items/{item_id}")

    assert resp.status == 401


def test_wrong_api_key_value_on_post_returns_401(api_context, item_payload_factory):
    headers = {"X-API-Key": "definitely-not-the-configured-key", "X-User-Role": "inventory_operator"}
    resp = api_context.post("/api/items", headers=headers, data=item_payload_factory())
    assert resp.status == 401


# ---------------------------------------------------------------------------
# Rule: Authenticated requests are subject to role-based access control -> 403
# ---------------------------------------------------------------------------

def test_missing_role_header_with_valid_key_returns_403(
    api_context, valid_headers_factory, item_payload_factory
):
    headers = valid_headers_factory(role=None)
    resp = api_context.post("/api/items", headers=headers, data=item_payload_factory())
    assert resp.status == 403


def test_unrecognized_role_value_returns_403(
    api_context, valid_headers_factory, item_payload_factory
):
    headers = valid_headers_factory(role="warehouse_intern")
    resp = api_context.post("/api/items", headers=headers, data=item_payload_factory())
    assert resp.status == 403


def test_inventory_operator_delete_returns_403(
    api_context, valid_headers_factory, existing_item
):
    headers = valid_headers_factory(role="inventory_operator")
    resp = api_context.delete(f"/api/items/{existing_item['id']}", headers=headers)
    assert resp.status == 403


# ---------------------------------------------------------------------------
# Rule: Roles permitted by the RBAC matrix succeed on their allowed verbs
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("role", ["inventory_operator", "supervisor", "administrator"])
def test_allowed_role_can_post(
    api_context, valid_headers_factory, item_payload_factory, role
):
    headers = valid_headers_factory(role=role)
    resp = api_context.post("/api/items", headers=headers, data=item_payload_factory())
    assert resp.status == 201, resp.text()
    assert resp.json()["sku"].startswith("PW-CAP44-")


@pytest.mark.parametrize("role", ["inventory_operator", "supervisor", "administrator"])
def test_allowed_role_can_patch(
    api_context, valid_headers_factory, existing_item, role
):
    headers = valid_headers_factory(role=role)
    resp = api_context.patch(
        f"/api/items/{existing_item['id']}", headers=headers, data={"quantity": 42}
    )
    assert resp.status == 200, resp.text()
    assert resp.json()["quantity"] == 42


@pytest.mark.parametrize("role", ["supervisor", "administrator"])
def test_allowed_role_can_delete(
    api_context, valid_headers_factory, existing_item, role
):
    headers = valid_headers_factory(role=role)
    resp = api_context.delete(f"/api/items/{existing_item['id']}", headers=headers)
    assert resp.status == 204


# ---------------------------------------------------------------------------
# Rule: Read endpoints remain unauthenticated
# ---------------------------------------------------------------------------

def test_unauthenticated_get_items_returns_200(api_context):
    resp = api_context.get("/api/items")
    assert resp.status == 200
    assert isinstance(resp.json(), list)


def test_unauthenticated_health_returns_200(api_context):
    resp = api_context.get("/api/health")
    assert resp.status == 200
    assert resp.json() == {"status": "ok"}
