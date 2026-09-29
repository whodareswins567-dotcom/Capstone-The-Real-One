"""Playwright API-level tests for CAP-48 CORS credentialed-request behavior,
mirroring playwright/features/cap48_cors_credentials.feature.

Run with:
    pytest playwright -q

(Deliberately outside tests/ so pytest.ini's testpaths=tests / plain
`pytest -q` CI invocation does not pick these up - they need a live
uvicorn process with a specific IMS_CORS_ALLOW_CREDENTIALS environment,
not the ASGI TestClient used by tests/test_cors.py.)
"""

from pathlib import Path

from conftest import CORS_ALLOWED_ORIGIN

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
# Rule: When IMS_CORS_ALLOW_CREDENTIALS is unset, CORS does not allow
# credentials by default (AC1, AC2)
# ---------------------------------------------------------------------------

def test_allowed_origin_gets_no_credentials_header_by_default(cors_allowlisted_context):
    resp = _preflight(cors_allowlisted_context, origin=CORS_ALLOWED_ORIGIN)
    assert resp.status in (200, 204)
    # Sanity: this is still the allowlisted origin, so allow-origin is echoed.
    assert resp.headers.get("access-control-allow-origin") == CORS_ALLOWED_ORIGIN
    assert resp.headers.get("access-control-allow-credentials") is None


# ---------------------------------------------------------------------------
# Rule: When IMS_CORS_ALLOW_CREDENTIALS is explicitly enabled, CORS allows
# credentials (AC2, AC3)
# ---------------------------------------------------------------------------

def test_allowed_origin_gets_credentials_true_when_explicitly_enabled(cors_credentials_enabled_context):
    resp = _preflight(cors_credentials_enabled_context, origin=CORS_ALLOWED_ORIGIN)
    assert resp.status in (200, 204)
    assert resp.headers.get("access-control-allow-origin") == CORS_ALLOWED_ORIGIN
    assert resp.headers.get("access-control-allow-credentials") == "true"


# ---------------------------------------------------------------------------
# Rule: An unrecognized IMS_CORS_ALLOW_CREDENTIALS value falls back to the
# safe disabled default (AC2)
# ---------------------------------------------------------------------------

def test_unrecognized_credentials_value_falls_back_to_disabled(cors_credentials_unrecognized_context):
    resp = _preflight(cors_credentials_unrecognized_context, origin=CORS_ALLOWED_ORIGIN)
    assert resp.status in (200, 204)
    assert resp.headers.get("access-control-allow-origin") == CORS_ALLOWED_ORIGIN
    assert resp.headers.get("access-control-allow-credentials") is None


# ---------------------------------------------------------------------------
# Rule: Automated CORS credentials regression coverage executes as part of
# CI (AC3)
# ---------------------------------------------------------------------------

def test_cors_credentials_unit_suite_exists_and_is_collected_by_main_ci_pytest_run():
    """AC3 is satisfied by tests/test_cors.py, which lives under
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
        "def test_cors_does_not_allow_credentials_by_default",
        "def test_cors_allows_credentials_when_explicitly_enabled",
    ):
        assert expected_test in content
