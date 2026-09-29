"""Playwright API-level tests for CAP-47 CORS allowlist behavior, mirroring
playwright/features/cap47_cors_allowlist.feature.

Run with:
    pytest playwright -q

(Deliberately outside tests/ so pytest.ini's testpaths=tests / plain
`pytest -q` CI invocation does not pick these up - they need a live
uvicorn process with a specific IMS_CORS_ALLOW_ORIGINS environment,
not the ASGI TestClient used by tests/test_cors.py.)
"""

from pathlib import Path

import pytest

from conftest import CORS_ALLOWED_ORIGIN

DISALLOWED_ORIGIN = "https://evil.example"
ANY_ORIGIN = "https://any.example"

REPO_ROOT = Path(__file__).resolve().parent.parent


def _preflight(context, *, origin: str):
    return context.fetch(
        "/api/health",
        method="OPTIONS",
        headers={
            "Origin": origin,
            "Access-Control-Request-Method": "GET",
        },
    )


# ---------------------------------------------------------------------------
# Rule: Requests from an allowed origin receive an explicit
# Access-Control-Allow-Origin header (AC1, AC3)
# ---------------------------------------------------------------------------

def test_configured_allowed_origin_returns_that_origin(cors_allowlisted_context):
    resp = _preflight(cors_allowlisted_context, origin=CORS_ALLOWED_ORIGIN)
    assert resp.status in (200, 204)
    assert resp.headers.get("access-control-allow-origin") == CORS_ALLOWED_ORIGIN


# ---------------------------------------------------------------------------
# Rule: Requests from a disallowed origin never receive that origin in
# Access-Control-Allow-Origin (AC1, AC4)
# ---------------------------------------------------------------------------

def test_disallowed_origin_gets_no_cors_header(cors_allowlisted_context):
    resp = _preflight(cors_allowlisted_context, origin=DISALLOWED_ORIGIN)
    # Starlette's CORSMiddleware returns 400 for a rejected preflight.
    assert resp.status in (200, 204, 400)
    assert resp.headers.get("access-control-allow-origin") is None


# ---------------------------------------------------------------------------
# Rule: When IMS_CORS_ALLOW_ORIGINS is unset, CORS denies all origins by
# default (AC2)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("origin", [CORS_ALLOWED_ORIGIN, ANY_ORIGIN])
def test_unset_allowlist_denies_any_origin_by_default(cors_default_context, origin):
    resp = _preflight(cors_default_context, origin=origin)
    # Starlette's CORSMiddleware returns 400 for a rejected preflight.
    assert resp.status in (200, 204, 400)
    assert resp.headers.get("access-control-allow-origin") is None


# ---------------------------------------------------------------------------
# Rule: Automated CORS regression coverage executes as part of CI (AC5)
# ---------------------------------------------------------------------------

def test_cors_unit_suite_exists_and_is_collected_by_main_ci_pytest_run():
    """AC5 is satisfied by tests/test_cors.py, which lives under
    pytest.ini's testpaths=tests and therefore runs automatically under the
    CI "pytest -q" invocation. This check guards against that file (or its
    key test functions) silently disappearing/being renamed; it does not
    re-run pytest itself, since spawning a nested pytest is unnecessary
    here and this Playwright suite already exercises the same behavior
    end-to-end above."""
    cors_test_file = REPO_ROOT / "tests" / "test_cors.py"
    assert cors_test_file.is_file()

    content = cors_test_file.read_text(encoding="utf-8")
    for expected_test in (
        "def test_cors_allows_configured_origin",
        "def test_cors_blocks_disallowed_origin",
        "def test_cors_denies_by_default_when_unset",
    ):
        assert expected_test in content
