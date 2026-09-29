from __future__ import annotations

import os
from enum import Enum

from fastapi import Depends, HTTPException, Request



class Role(str, Enum):
    OPERATOR = "operator"
    SUPERVISOR = "supervisor"
    ADMIN = "admin"



def _extract_bearer_token(auth_header: str | None) -> str | None:
    if not auth_header:
        return None

    parts = auth_header.split()
    if len(parts) != 2:
        return None
    if parts[0].lower() != "bearer":
        return None
    return parts[1]



def _get_token_for_role(role: Role) -> str | None:
    if role == Role.OPERATOR:
        return os.getenv("IMS_OPERATOR_TOKEN")
    if role == Role.SUPERVISOR:
        return os.getenv("IMS_SUPERVISOR_TOKEN")
    if role == Role.ADMIN:
        return os.getenv("IMS_ADMIN_TOKEN")
    return None



def get_role_from_token(token: str) -> Role | None:
    for role in (Role.OPERATOR, Role.SUPERVISOR, Role.ADMIN):
        expected = _get_token_for_role(role)
        if expected and token == expected:
            return role
    return None



def get_current_role(request: Request) -> Role:
    token = _extract_bearer_token(request.headers.get("Authorization"))
    if not token:
        raise HTTPException(status_code=401, detail="Missing or invalid authentication")

    role = get_role_from_token(token)
    if not role:
        raise HTTPException(status_code=401, detail="Invalid authentication")

    return role



def require_roles(*allowed_roles: Role):
    allowed = set(allowed_roles)

    def _dependency(role: Role = Depends(get_current_role)) -> Role:
        if role not in allowed:
            raise HTTPException(status_code=403, detail="Forbidden")
        return role

    return _dependency
