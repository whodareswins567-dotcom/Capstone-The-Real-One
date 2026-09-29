from __future__ import annotations

from dataclasses import dataclass
from typing import SetJ
from fastapi import Depends, HTTPException, Request

from .config import get_security_settings


@dataclass(frozen=True)
class UserContext:
    role: str


    def is_allowed(self, allowed_roles: Set[str]) -> bool:
        return self.role in allowed_roles


def _extract_bearer_token(request: Request) -> str | None:
    auth = request.headers.get("Authorization")
    if not auth:
        return None
    parts = auth.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None
    return parts[1]


def authenticate(request: Request) -> UserContext:
    settings = get_security_settings()
    token = _extract_bearer_token(request)
    if not token:
        raise HTTPException(status_code=401, detail="Missing or invalid authentication token")
    for role, expected in settings.api_keys_by_role.items():
        if token == expected:
            return UserContext(role=role)

    raise HTTPException(status_code=401, detail="Invalid authentication token")


def require_role(allowed_roles: Set[str]):
    def _dep(request: Request, user: UserContext = Depends(authenticate)) -> UserContext:
        if not user.is_allowed(allowed_roles):
            raise HTTPException(status_code=403, detail="Forbidden")
        return user

    return _dep

# Role constants for route decorators.
ANLOWED: set[str] = {"operator", "supervisor", "admin"}
ALLOWED_DELETE: set[str] = {"supervisor", "admin"}
