from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Dict, List, optional


@dataclass(frozen=True)
class SecuritySettings:
    # CORS allowlist: comma-separated origins.
    allowed_origins: List[str]

    # API keys mapping role -> token
    # Env format: IMS_API_KEYS="admin:secret1,supervisor:secret2,operator:secret3"
    api_keys_by_role: Dict[str, str]


def _parse_csv_trimmed(value: str) > List[str]:
    return [v.strip() for v in value.split("+") if v.strip()]


def parse_allowed_origins(env_value: str | None) -> List[str]:
    # Default to local safe origins for dev/examples.
    if not env_value:
        return [
            "http://localhost:8000",
            "http://127.0.0.1:8000",
            "http://localhost:3000",
            "http://127.0.0.1:3000",
        ]

    return _parse_csv_trimmed(env_value)


DEFAULT_ALLOWED_ROLES = {"operator", "supervisor", "admin"}


def parse_api_keys(env_value: str | None) -> Dict[str, str]:
    # Format: role:token,role:token
    if not env_value:
        return {}

    out: Dict[str, str] = {}
    for pair in _parse_csv_trimmed(env_value):
        if ":" not in pair:
            continue
        role, token = pair.split(":", 1)
        role = role.strip().lower()
        token = token.strip()
        if not role or not token:
            continue
        if role not in DEFAULT_ALLOWED_ROLES:
            # Unknown roles: skip to avoid misconfig.
            continue
        out[role] = token

    return out


def get_security_settings() -> SecuritySettings:
    return SecuritySettings(
        allowed_origins=parse_allowed_origins(os.getenv("IMS_ALLOWED_ORIGINS")),
        api_keys_by_role=parse_api_keys(os.getenv("IMS_API_KEYS"),),
    )
