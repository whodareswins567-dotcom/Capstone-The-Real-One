Feature: Authentication and RBAC for inventory write endpoints (CAP-46)
  As the Inventory Management System
  I want to protect write operations on /api/items with bearer-token
  authentication and role-based access control
  So that only authorized roles can create, update, or delete inventory items,
  while read access remains open to everyone

  # Traceability: CAP-46 acceptance criteria 1-4
  # AC1: Unauthenticated or invalid-bearer-token write requests -> 401
  # AC2: Authenticated but under-privileged role on write ops -> 403
  # AC3: RBAC matrix - operator/supervisor/admin can POST/PATCH;
  #      only admin can DELETE
  # AC4: Automated tests cover both 401 and 403 outcomes

  Background:
    Given the inventory API is running with configured "IMS_OPERATOR_TOKEN",
    "IMS_SUPERVISOR_TOKEN" and "IMS_ADMIN_TOKEN" bearer tokens

  Rule: Unauthenticated or misauthenticated requests to write endpoints return 401

    Scenario Outline: Missing Authorization header on a write endpoint returns 401
      Given no "Authorization" header is supplied
      When I send a "<method>" request to "<endpoint>"
      Then the response status is 401

      Examples:
        | method | endpoint                 |
        | POST   | /api/items                |
        | PATCH  | /api/items/{existing_id}  |
        | DELETE | /api/items/{existing_id}  |

    Scenario Outline: Garbage bearer token on a write endpoint returns 401
      Given the "Authorization" header is "Bearer not-a-real-token"
      When I send a "<method>" request to "<endpoint>"
      Then the response status is 401

      Examples:
        | method | endpoint                 |
        | POST   | /api/items                |
        | PATCH  | /api/items/{existing_id}  |
        | DELETE | /api/items/{existing_id}  |

  Rule: Authenticated requests are subject to role-based access control

    Scenario Outline: Authenticated but forbidden role attempting DELETE returns 403

      Given a valid bearer token for role "<role>" is supplied
      And an inventory item exists
      When I send a "DELETE" request to "/api/items/{existing_id}"
      Then the response status is 403

      Examples:
        | role       |
        | operator   |
        | supervisor |

  Rule: Roles permitted by the RBAC matrix succeed on their allowed write verbs

    Scenario Outline: Allowed role can POST a new item

      Given a valid bearer token for role "<role>" is supplied
      When I send a "POST" request to "/api/items" with a unique SKU payload
      Then the response status is 201

      Examples:
        | role       |
        | operator   |
        | supervisor |
        | admin      |

    Scenario Outline: Allowed role can PATCH an existing item

      Given a valid bearer token for role "<role>" is supplied
      And an inventory item exists
      When I send a "PATCH" request to "/api/items/{existing_id}" updating the quantity
      Then the response status is 200

      Examples:
        | role       |
        | operator   |
        | supervisor |
        | admin      |

    Scenario: Admin can DELETE an existing item

      Given a valid bearer token for role "admin" is supplied
      And an inventory item exists
      When I send a "DELETE" request to "/api/items/{existing_id}"
      Then the response status is 204

  Rule: Read endpoints remain unauthenticated

    Scenario Outline: Unauthenticated read requests succeed
      Given no "Authorization" header is supplied
      When I send a "GET" request to "<endpoint>"
      Then the response status is 200

      Examples:
        | endpoint    |
        | /api/items  |
        | /api/health |
