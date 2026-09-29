Feature: Environment-driven CORS allowlist for the inventory API (CAP-47)
  As the Inventory Management System
  I want CORS behavior to be driven by an environment-configured allowlist
  instead of a wildcard
  So that only explicitly trusted browser origins can make cross-origin
  requests to the API, and origins not on that list are refused by default

  # Traceability: CAP-47 acceptance criteria 1-5
  # AC1: Configurable allowlist - CORS middleware uses an environment
  #      variable allowlist ("IMS_CORS_ALLOW_ORIGINS") instead of ["*"]
  # AC2: Safe default behavior - if IMS_CORS_ALLOW_ORIGINS is unset/empty,
  #      CORS denies all origins by default (no wildcard fallback)
  # AC3: Requests from an allowed origin receive the expected
  #      Access-Control-Allow-Origin header
  # AC4: Requests from a disallowed origin do not receive
  #      Access-Control-Allow-Origin for that origin
  # AC5: CORS tests run as part of pytest in CI - satisfied today by
  #      tests/test_cors.py (collected under pytest.ini's testpaths=tests);
  #      this Playwright suite adds complementary real-HTTP end-to-end
  #      coverage of the same behavior, run explicitly via
  #      "pytest playwright -q"

  Background:
    Given the inventory API is running as a live server

  Rule: Requests from an allowed origin receive an explicit Access-Control-Allow-Origin header

    Scenario Outline: Preflight from a configured allowed origin returns that origin
      Given the inventory API is configured with "IMS_CORS_ALLOW_ORIGINS" set to "<allowed_origins>"
      When I send an OPTIONS preflight request to "/api/health" with "Origin" "<origin>" and "Access-Control-Request-Method" "GET"
      Then the response includes an "Access-Control-Allow-Origin" header with value "<origin>"

      Examples:
        | allowed_origins          | origin                   |
        | https://allowed.example  | https://allowed.example  |

  Rule: Requests from a disallowed origin never receive that origin in Access-Control-Allow-Origin

    Scenario Outline: Preflight from an origin not in the allowlist gets no CORS header
      Given the inventory API is configured with "IMS_CORS_ALLOW_ORIGINS" set to "<allowed_origins>"
      When I send an OPTIONS preflight request to "/api/health" with "Origin" "<origin>" and "Access-Control-Request-Method" "GET"
      Then the response does not include an "Access-Control-Allow-Origin" header

      Examples:
        | allowed_origins          | origin                 |
        | https://allowed.example  | https://evil.example   |

  Rule: When IMS_CORS_ALLOW_ORIGINS is unset, CORS denies all origins by default

    Scenario Outline: Preflight against a server with no CORS allowlist configured gets no CORS header
      Given the inventory API is running with "IMS_CORS_ALLOW_ORIGINS" unset
      When I send an OPTIONS preflight request to "/api/health" with "Origin" "<origin>" and "Access-Control-Request-Method" "GET"
      Then the response does not include an "Access-Control-Allow-Origin" header

      Examples:
        | origin                   |
        | https://allowed.example  |
        | https://any.example      |

  Rule: Automated CORS regression coverage executes as part of CI

    Scenario: CORS tests are collected and executed by the main pytest CI invocation
      Given the "tests/test_cors.py" suite validates allowed, disallowed and default-unset CORS behavior
      When CI runs "pytest -q"
      Then the CORS tests are collected and executed automatically
      And this Playwright suite provides complementary end-to-end coverage runnable via "pytest playwright -q"
