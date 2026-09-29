Feature: Environment-driven CORS credentialed-request behavior for the inventory API (CAP-48)
  As the Inventory Management System
  I want CORS credentialed-request behavior to be driven by an explicit
  environment toggle instead of being unconditionally enabled
  So that browsers are only told credentialed cross-origin requests
  (cookies/auth headers) are permitted when that has been intentionally
  configured, and the safe default is to not allow credentials

  # Traceability: CAP-48 acceptance criteria 1-3 (see task/CAP-48.md)
  # AC1: A clear decision is recorded stating whether allow_credentials must
  #      be enabled or disabled by default - the recorded decision is: safe
  #      default of disabled (False) unless explicitly opted in via
  #      IMS_CORS_ALLOW_CREDENTIALS.
  # AC2: CORS middleware configuration in backend/main.py matches that
  #      decision - allow_credentials is parsed from IMS_CORS_ALLOW_CREDENTIALS
  #      via _parse_cors_allow_credentials(), defaulting to False.
  # AC3: At least one automated test asserts the presence/absence of
  #      credentialed CORS behavior consistent with the decision - satisfied
  #      today by tests/test_cors.py (collected under pytest.ini's
  #      testpaths=tests); this Playwright suite adds complementary real-HTTP
  #      end-to-end coverage of the same behavior, run explicitly via
  #      "pytest playwright -q".

  Background:
    Given the inventory API is running as a live server

  Rule: When IMS_CORS_ALLOW_CREDENTIALS is unset, CORS does not allow credentials by default

    Scenario Outline: Preflight from an allowed origin gets no Access-Control-Allow-Credentials header by default
      Given the inventory API is configured with "IMS_CORS_ALLOW_ORIGINS" set to "<allowed_origins>"
      And "IMS_CORS_ALLOW_CREDENTIALS" is unset
      When I send an OPTIONS preflight request to "/api/health" with "Origin" "<origin>" and "Access-Control-Request-Method" "GET"
      Then the response does not include an "Access-Control-Allow-Credentials" header

      Examples:
        | allowed_origins          | origin                   |
        | https://allowed.example  | https://allowed.example  |

  Rule: When IMS_CORS_ALLOW_CREDENTIALS is explicitly enabled, CORS allows credentials

    Scenario Outline: Preflight from an allowed origin returns Access-Control-Allow-Credentials true when explicitly enabled
      Given the inventory API is configured with "IMS_CORS_ALLOW_ORIGINS" set to "<allowed_origins>"
      And "IMS_CORS_ALLOW_CREDENTIALS" set to "<allow_credentials_value>"
      When I send an OPTIONS preflight request to "/api/health" with "Origin" "<origin>" and "Access-Control-Request-Method" "GET"
      Then the response includes an "Access-Control-Allow-Credentials" header with value "true"

      Examples:
        | allowed_origins          | origin                   | allow_credentials_value |
        | https://allowed.example  | https://allowed.example  | true                    |

  Rule: An unrecognized IMS_CORS_ALLOW_CREDENTIALS value falls back to the safe disabled default

    Scenario Outline: Preflight from an allowed origin with an unrecognized credentials value gets no Access-Control-Allow-Credentials header
      Given the inventory API is configured with "IMS_CORS_ALLOW_ORIGINS" set to "<allowed_origins>"
      And "IMS_CORS_ALLOW_CREDENTIALS" set to "<allow_credentials_value>"
      When I send an OPTIONS preflight request to "/api/health" with "Origin" "<origin>" and "Access-Control-Request-Method" "GET"
      Then the response does not include an "Access-Control-Allow-Credentials" header

      Examples:
        | allowed_origins          | origin                   | allow_credentials_value |
        | https://allowed.example  | https://allowed.example  | nope                    |

  Rule: Automated CORS credentials regression coverage executes as part of CI

    Scenario: CORS credentials tests are collected and executed by the main pytest CI invocation
      Given the "tests/test_cors.py" suite validates default-disabled and explicitly-enabled credentialed CORS behavior
      When CI runs "pytest -q"
      Then the CORS credentials tests are collected and executed automatically
      And this Playwright suite provides complementary end-to-end coverage runnable via "pytest playwright -q"
