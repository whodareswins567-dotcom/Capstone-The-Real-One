"""RBAC coverage for the write endpoints (POST/PATCH/DELETE /api/items).

The permission matrix (per CAP-46):
- POST /api/items: operator, supervisor, admin allowed
- PATCH /api/items/{item_id}: operator, supervisor, admin allowed
- DELETE /api/items/{item_id}: admin only
"""
import pytest


def _create_payload(sku: str) -> dict:
    return {
        "sku": sku,
        "name": "RBAC Test Item",
        "category": "Misc",
        "quantity": 1,
        "reorder_level": 1,
        "location": "A1",
        "notes": "",
    }


@pytest.mark.parametrize(
    "method, path, json_body",
    [
        ("post", "/api/items", _create_payload("SKU-9000")),
        ("patch", "/api/items/1", {"quantity": 2}),
        ("delete", "/api/items/1", None),
    ],
)
def test_write_endpoint_requires_auth_header(client, method, path, json_body):
    call = getattr(client, method)
    resp = call(path, json=json_body) if json_body is not None else call(path)
    assert resp.status_code == 401


@pytest.mark.parametrize(
    "method, path, json_body",
    [
        ("post", "/api/items", _create_payload("SKU-9001")),
        ("patch", "/api/items/1", {"quantity": 2}),
        ("delete", "/api/items/1", None),
    ],
)
def test_write_endpoint_rejects_invalid_token(client, method, path, json_body):
    bad_headers = {"Authorization": "Bearer not-a-real-token"}
    call = getattr(client, method)
    resp = (
        call(path, json=json_body, headers=bad_headers)
        if json_body is not None
        else call(path, headers=bad_headers)
    )
    assert resp.status_code == 401


@pytest.mark.parametrize("role", ["operator", "supervisor"])
def test_delete_item_forbidden_for_non_admin_roles(client, headers, role):
    create = client.post(
        "/api/items",
        json=_create_payload(f"SKU-9002-{role}"),
        headers=headers["admin"],
    )
    assert create.status_code == 201
    item_id = create.json()["id"]

    resp = client.delete(f"/api/items/{item_id}", headers=headers[role])
    assert resp.status_code == 403


@pytest.mark.parametrize("role", ["operator", "supervisor", "admin"])
def test_create_item_allowed_for_every_role(client, headers, role):
    resp = client.post(
        "/api/items",
        json=_create_payload(f"SKU-9003-{role}"),
        headers=headers[role],
    )
    assert resp.status_code == 201
    assert resp.json()["sku"] == f"SKU-9003-{role}"


@pytest.mark.parametrize("role", ["operator", "supervisor", "admin"])
def test_patch_item_allowed_for_every_role(client, headers, role):
    create = client.post(
        "/api/items",
        json=_create_payload(f"SKU-9004-{role}"),
        headers=headers["admin"],
    )
    assert create.status_code == 201
    item_id = create.json()["id"]

    resp = client.patch(
        f"/api/items/{item_id}",
        json={"quantity": 7},
        headers=headers[role],
    )
    assert resp.status_code == 200
    assert resp.json()["quantity"] == 7


def test_delete_item_allowed_for_admin(client, headers):
    create = client.post(
        "/api/items",
        json=_create_payload("SKU-9005-admin"),
        headers=headers["admin"],
    )
    assert create.status_code == 201
    item_id = create.json()["id"]

    resp = client.delete(f"/api/items/{item_id}", headers=headers["admin"])
    assert resp.status_code == 204
