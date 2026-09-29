"""Fixtures for API-level Playwright tests against the FastAPI app.

These tests exercise CAP-46 auth/RBAC behavior, CAP-47 CORS-allowlist behavior, and
CAP-48 CORS credentialed-request behavior over real HTTP (not the ASGI TestClient used by tests/), by
launching `uvicorn backend.main:app` as a subprocess against an isolated
temp SQLite DB, then driving it with Playwright's APIRequestContext (no
browser binaries required).

Deliberately kept outside tests/ (pytest.ini pins testpaths=tests) so the
existing `pytest -q` CI invocation is unaffected. Run these explicitly:

    pytest playwright -q
"""

from __future__ import annotations

import os
import socket
import subprocess
import sys
import time
import uuid
import urllib.error
import urllib.request
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
OPERATOR_TOKEN = "pw-cap46-operator-token"
SUPERVISOR_TOKEN = "pw-cap46-supervisor-token"
ADMIN_TOKEN = "pw-cap46-admin-token"

ROLE_TOKENS = {
    "operator": OPERATOR_TOKEN,
    "supervisor": SUPERVISOR_TOKEN,
    "admin": ADMIN_TOKEN,
}

# CAP-47: origin baked into the "allowlisted" live server's
# IMS_CORS_ALLOW_ORIGINS env var. Kept here (rather than in the test file)
# so fixture setup and test assertions can't drift apart.
CORS_ALLOWED_ORIGIN = "https://allowed.example"

# CAP-48: value baked into the "credentials enabled" live server's
# IMS_CORS_ALLOW_CREDENTIALS env var, and a deliberately unrecognized value
# used to exercise the safe-default parsing fallback.
CORS_ALLOW_CREDENTIALS_VALUE = "true"
CORS_ALLOW_CREDENTIALS_UNRECOGNIZED_VALUE = "nope"


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _wait_for_health(base_url: str, proc: subprocess.Popen, timeout: float = 15.0) -> None:
    deadline = time.time() + timeout
    last_error: Exception | None = None
    while time.time() < deadline:
        if proc.poll() is not None:
            output = proc.stdout.read() if proc.stdout else ""
            raise RuntimeError(
                f"uvicorn exited early with code {proc.returncode}.\nOutput:\n{output}"
            )
        try:
            with urllib.request.urlopen(f"{base_url}/api/health", timeout=1) as resp:
                if resp.status == 200:
                    return
        except (urllib.error.URLError, ConnectionError) as exc:
            last_error = exc
            time.sleep(0.2)
    raise RuntimeError(f"Server did not become healthy in time: {last_error}")


def _launch_uvicorn(db_path: Path, port: int, env: dict[str, str]):
    """Launch `backend.main:app` as a subprocess with the given env.

    Shared by every live-server fixture in this module (CAP-46 and CAP-47)
    so each one only has to decide which env vars to set/unset, not
    re-implement process launch/health-wait/teardown.
    """
    env = dict(env)
    env["INVENTORY_DB_PATH"] = str(db_path)

    proc = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "backend.main:app",
            "--host",
            "127.0.0.1",
            "--port",
            str(port),
            "--log-level",
            "warning",
        ],
        cwd=str(REPO_ROOT),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    return proc


def _run_server(db_prefix: str, tmp_path_factory, env: dict[str, str]):
    """Generator body shared by the session-scoped live-server fixtures:
    start uvicorn, wait for health, yield the base URL, then tear down."""
    db_path = tmp_path_factory.mktemp(db_prefix) / "inventory.db"
    port = _free_port()
    base_url = f"http://127.0.0.1:{port}"

    proc = _launch_uvicorn(db_path, port, env)

    try:
        _wait_for_health(base_url, proc)
        yield base_url
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=5)


@pytest.fixture(scope="session")
def role_tokens() -> dict[str, str]:
    return ROLE_TOKENS


@pytest.fixture(scope="session")
def live_server(tmp_path_factory, role_tokens):
    """Start a real backend.main:app instance on a free port, configured
    with CAP-46 role tokens (auth/RBAC suite)."""
    env = os.environ.copy()
    env["IMS_OPERATOR_TOKEN"] = role_tokens["operator"]
    env["IMS_SUPERVISOR_TOKEN"] = role_tokens["supervisor"]
    env["IMS_ADMIN_TOKEN"] = role_tokens["admin"]

    yield from _run_server("cap46-pw-db", tmp_path_factory, env)


@pytest.fixture(scope="session")
def cors_allowlisted_server(tmp_path_factory):
    """CAP-47: a live server started with IMS_CORS_ALLOW_ORIGINS set to a
    single known origin (CORS_ALLOWED_ORIGIN), used to verify that origin
    is echoed back and that any other origin is not.

    Also reused by CAP-48: IMS_CORS_ALLOW_CREDENTIALS is left unset here
    (defensively popped, in case it happens to be set in the ambient
    environment), so this same server doubles as the safe
    credentials-disabled-by-default baseline."""
    env = os.environ.copy()
    env["IMS_CORS_ALLOW_ORIGINS"] = CORS_ALLOWED_ORIGIN
    env.pop("IMS_CORS_ALLOW_CREDENTIALS", None)

    yield from _run_server("cap47-pw-allowlisted-db", tmp_path_factory, env)


@pytest.fixture(scope="session")
def cors_default_server(tmp_path_factory):
    """CAP-47: a live server started with IMS_CORS_ALLOW_ORIGINS entirely
    unset, used to verify the safe (deny-by-default) fallback."""
    env = os.environ.copy()
    env.pop("IMS_CORS_ALLOW_ORIGINS", None)

    yield from _run_server("cap47-pw-default-db", tmp_path_factory, env)


@pytest.fixture(scope="session")
def cors_credentials_enabled_server(tmp_path_factory):
    """CAP-48: a live server started with IMS_CORS_ALLOW_ORIGINS set to a
    single known origin (CORS_ALLOWED_ORIGIN) and IMS_CORS_ALLOW_CREDENTIALS
    explicitly enabled, used to verify Access-Control-Allow-Credentials is
    present and true when the toggle is opted in."""
    env = os.environ.copy()
    env["IMS_CORS_ALLOW_ORIGINS"] = CORS_ALLOWED_ORIGIN
    env["IMS_CORS_ALLOW_CREDENTIALS"] = CORS_ALLOW_CREDENTIALS_VALUE

    yield from _run_server("cap48-pw-credentials-enabled-db", tmp_path_factory, env)


@pytest.fixture(scope="session")
def cors_credentials_unrecognized_server(tmp_path_factory):
    """CAP-48: a live server started with IMS_CORS_ALLOW_ORIGINS set to a
    single known origin (CORS_ALLOWED_ORIGIN) and IMS_CORS_ALLOW_CREDENTIALS
    set to an unrecognized value, used to verify the safe-default parsing
    fallback (treated the same as disabled/unset)."""
    env = os.environ.copy()
    env["IMS_CORS_ALLOW_ORIGINS"] = CORS_ALLOWED_ORIGIN
    env["IMS_CORS_ALLOW_CREDENTIALS"] = CORS_ALLOW_CREDENTIALS_UNRECOGNIZED_VALUE

    yield from _run_server("cap48-pw-credentials-unrecognized-db", tmp_path_factory, env)


@pytest.fixture()
def api_context(playwright, live_server):
    """A Playwright APIRequestContext pinned to the live server's base URL."""
    context = playwright.request.new_context(base_url=live_server)
    yield context
    context.dispose()


@pytest.fixture()
def cors_allowlisted_context(playwright, cors_allowlisted_server):
    """APIRequestContext pinned to the CAP-47 allowlisted live server."""
    context = playwright.request.new_context(base_url=cors_allowlisted_server)
    yield context
    context.dispose()


@pytest.fixture()
def cors_default_context(playwright, cors_default_server):
    """APIRequestContext pinned to the CAP-47 no-allowlist-configured live server."""
    context = playwright.request.new_context(base_url=cors_default_server)
    yield context
    context.dispose()


@pytest.fixture()
def cors_credentials_enabled_context(playwright, cors_credentials_enabled_server):
    """APIRequestContext pinned to the CAP-48 credentials-enabled live server."""
    context = playwright.request.new_context(base_url=cors_credentials_enabled_server)
    yield context
    context.dispose()


@pytest.fixture()
def cors_credentials_unrecognized_context(playwright, cors_credentials_unrecognized_server):
    """APIRequestContext pinned to the CAP-48 unrecognized-credentials-value live server."""
    context = playwright.request.new_context(base_url=cors_credentials_unrecognized_server)
    yield context
    context.dispose()


@pytest.fixture()
def valid_headers_factory(role_tokens):
    def _make(role: str | None) -> dict[str, str]:
        if role is None:
            return {}
        token = role_tokens[role]
        return {"Authorization": f"Bearer {token}"}

    return _make


@pytest.fixture()
def item_payload_factory():
    """Unique SKU per call (not just per fixture instantiation) - the
    live_server DB persists across the whole test session, so a counter
    that resets per-test would collide across different test functions."""

    def _make(**overrides) -> dict:
        payload = {
            "sku": f"PW-CAP46-{uuid.uuid4().hex[:12]}",
            "name": "Playwright Test Item",
            "category": "QA",
            "quantity": 5,
            "reorder_level": 1,
            "location": "QA Bench",
            "notes": "Created by Playwright CAP-46 auth/RBAC suite",
        }
        payload.update(overrides)
        return payload

    return _make


@pytest.fixture()
def existing_item(api_context, valid_headers_factory, item_payload_factory):
    """Create an item with a fully-privileged role so PATCH/DELETE scenarios
    have a known-good target regardless of which role is under test."""
    headers = valid_headers_factory("admin")
    payload = item_payload_factory()
    resp = api_context.post("/api/items", headers=headers, data=payload)
    assert resp.status == 201, f"setup failed: {resp.status} {resp.text()}"
    return resp.json()
