"""Lightweight authentication and authorization helpers.

This repo has deliberately minimal dependencies and no user store.
For CAP-44 we add a simple approach:
- Authenticate write requests with an API key header.
- Authorize write requests with a deliberately-simple role header.

Headers (write endpoints only):
- X-API-Key: must match env var INVENTORY_API_KEY
- X-User-Role: one of inventory_operator, supervisor, administrator

"""

from __future__ import annotations

import os
from dataclasses import dataclass
from enum import Enum

from fastapi import Depends, HTTPException, Request


API_KEY_HEADER = "X-API-Key"
ROLE_HEADER = "X-User-Role"
API_KEY_ENV_VAR = "INVENTORY_API_KEY"


class Role(str, Enum):
    INVENTORY_OPERATOR = "inventory_operator"
    SUPERVISOR = "supervisor"
    ADMINISTRATOR = "administrator"


@dataclass
class Principal:
    role: Role


def _invalid_credentials() -> HTTPException:
    # We deliberately return 401 for missing/bad api key.
    return HTTPException(status_code=401, detail="Unauthorized")


def _forbidden() -> HTTPException:
    # 403 is used for authenticated-but-unauthorized.
    return HTTPException(status_code=403, detail="Forbidden")


def require_api_key(request: Request) -> None:
    expected = os.getenv(API_KEY_ENV_VAR)
    provided = request.headers.get(API_KEY_HEADER)

    if not expected:
        # Fail closed: write endpoints require a configured key.
        raise _invalid_credentials()

    if not provided or provided != expected:
        raise _invalid_credentials()


def get_role_from_headers(request: Request) -> Role:
    raw = request.headers.get(ROLE_HEADER)
    if not raw:
        raise _forbidden()

    try:
        return Role(raw)
    except ValueError as exc:
        raise _forbidden() from exc


def require_roles(allowed_roles: set[Role]):
    """Build a FastAPI dependency that enforces auth + RBAC.

    -> 401 if X-API-Key is missing/bad
    -> 403 if role is disallowed (or missing)
    """

    def _dependency(request: Request) -> Principal:
        require_api_key(request)
        role = get_role_from_headers(request)
        if role not in allowed_roles:
            raise _forbidden()
        return Principal(role=role)

    return Depends(_dependency)
