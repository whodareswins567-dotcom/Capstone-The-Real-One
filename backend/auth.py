from __future__ import annotations

import hashlib
import hmac
import os
import secrets
import time
import uuid
from dataclasses import dataclass
from enum import Enum
from typing import Any

import jwt
from fastapi import Depends, HTTPException, Request

from .database import get_connection


class Role(str, Enum):
    OPERATOR = "operator"
    SUPERVISOR = "supervisor"
    ADMIN = "admin"


JWT_ALGORITHM = "HS256"
DEFAULT_TOKEN_TTL_SECONDS = 8 * 60 * 60  # 8 hours

# Safe-for-local-dev-only default. Production deployments MUST set
# IMS_JWT_SECRET explicitly - see README "Authentication" section.
_DEV_DEFAULT_JWT_SECRET = "dev-only-insecure-jwt-secret-change-me"

_PBKDF2_ITERATIONS = 120_000


def _get_jwt_secret() -> str:
    return os.getenv("IMS_JWT_SECRET", _DEV_DEFAULT_JWT_SECRET)


def _get_token_ttl_seconds() -> int:
    raw = os.getenv("IMS_JWT_TTL_SECONDS", "")
    if not raw:
        return DEFAULT_TOKEN_TTL_SECONDS
    try:
        return int(raw)
    except ValueError:
        return DEFAULT_TOKEN_TTL_SECONDS


# ---------------------------------------------------------------------------
# Password hashing (stdlib PBKDF2-HMAC-SHA256; no third-party dependency)
# ---------------------------------------------------------------------------


def hash_password(password: str, salt: bytes | None = None) -> str:
    """Hash a password, returning a combined 'salt_hex$hash_hex' string.

    A random 16-byte salt is generated per call unless one is explicitly
    supplied (used by verify_password to re-derive with the stored salt).
    """
    salt = salt or secrets.token_bytes(16)
    derived = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, _PBKDF2_ITERATIONS)
    return f"{salt.hex()}${derived.hex()}"


def verify_password(password: str, stored: str) -> bool:
    """Constant-time comparison of a plaintext password against a stored hash."""
    try:
        salt_hex, hash_hex = stored.split("$", 1)
        salt = bytes.fromhex(salt_hex)
        expected = bytes.fromhex(hash_hex)
    except (ValueError, AttributeError):
        return False

    derived = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, _PBKDF2_ITERATIONS)
    return hmac.compare_digest(derived, expected)


# ---------------------------------------------------------------------------
# JWT issuance / verification
# ---------------------------------------------------------------------------


def create_access_token(user_id: int, username: str, role: Role) -> tuple[str, str]:
    """Create a signed JWT for an authenticated identity. Returns (token, jti)."""
    jti = uuid.uuid4().hex
    now = int(time.time())
    payload = {
        "sub": username,
        "uid": user_id,
        "role": role.value,
        "jti": jti,
        "iat": now,
        "exp": now + _get_token_ttl_seconds(),
    }
    token = jwt.encode(payload, _get_jwt_secret(), algorithm=JWT_ALGORITHM)
    return token, jti


def _decode_token(token: str) -> dict[str, Any]:
    try:
        return jwt.decode(token, _get_jwt_secret(), algorithms=[JWT_ALGORITHM])
    except jwt.PyJWTError as exc:
        raise HTTPException(status_code=401, detail="Invalid or expired authentication") from exc


def _extract_bearer_token(auth_header: str | None) -> str | None:
    if not auth_header:
        return None

    parts = auth_header.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None
    return parts[1]


def _is_token_revoked(request: Request, jti: str) -> bool:
    db_path = getattr(request.app.state, "db_path", None)
    with get_connection(db_path) as connection:
        row = connection.execute(
            "SELECT 1 FROM revoked_tokens WHERE jti = ?", (jti,)
        ).fetchone()
    return row is not None


@dataclass(frozen=True)
class Identity:
    """The authenticated identity resolved from a validated JWT."""

    user_id: int
    username: str
    role: Role
    jti: str
    exp: int


def get_current_identity(request: Request) -> Identity:
    """Resolve the authenticated identity from the request's bearer token.

    Raises 401 for a missing/malformed header, an invalid/expired JWT, or a
    token whose jti has been revoked (see POST /api/auth/logout).
    """
    token = _extract_bearer_token(request.headers.get("Authorization"))
    if not token:
        raise HTTPException(status_code=401, detail="Missing or invalid authentication")

    payload = _decode_token(token)

    jti = payload.get("jti")
    role_value = payload.get("role")
    username = payload.get("sub")
    user_id = payload.get("uid")

    if not jti or not role_value or not username or user_id is None:
        raise HTTPException(status_code=401, detail="Invalid authentication")

    try:
        role = Role(role_value)
    except ValueError as exc:
        raise HTTPException(status_code=401, detail="Invalid authentication") from exc

    if _is_token_revoked(request, jti):
        raise HTTPException(status_code=401, detail="Token has been revoked")

    return Identity(user_id=user_id, username=username, role=role, jti=jti, exp=payload.get("exp", 0))


def get_current_role(identity: Identity = Depends(get_current_identity)) -> Role:
    return identity.role


def require_roles(*allowed_roles: Role):
    allowed = set(allowed_roles)

    def _dependency(role: Role = Depends(get_current_role)) -> Role:
        if role not in allowed:
            raise HTTPException(status_code=403, detail="Forbidden")
        return role

    return _dependency


# ---------------------------------------------------------------------------
# Login / logout support
# ---------------------------------------------------------------------------


def authenticate_user(request: Request, username: str, password: str) -> tuple[str, Role]:
    """Verify credentials against the users table and issue a JWT.

    Returns (token, role). Raises 401 on any username/password mismatch -
    the same generic message is used for "no such user" and "wrong
    password" so the endpoint doesn't leak which one failed.
    """
    db_path = getattr(request.app.state, "db_path", None)
    with get_connection(db_path) as connection:
        row = connection.execute(
            "SELECT id, username, password_hash, role FROM users WHERE username = ?",
            (username,),
        ).fetchone()

    if row is None or not verify_password(password, row["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    role = Role(row["role"])
    token, _jti = create_access_token(row["id"], row["username"], role)
    return token, role


def revoke_current_token(request: Request, identity: Identity) -> None:
    """Record the given identity's jti as revoked so it can no longer be used."""
    db_path = getattr(request.app.state, "db_path", None)
    with get_connection(db_path) as connection:
        connection.execute(
            "INSERT OR IGNORE INTO revoked_tokens (jti, expires_at) VALUES (?, ?)",
            (identity.jti, identity.exp),
        )
