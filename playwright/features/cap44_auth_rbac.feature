Feature: Authentication and RBAC for inventory write endpoints (CAP-44)
  As the Inventory Management System
  I want to protect write operations on /api/items with API-key authentication
  and role-based access control
  So that only authorized roles can create, update, or delete inventory items,
  while read access remains open to everyone

  # Traceability: CAP-44 acceptance criteria 1-4
  # AC1: Unauthenticated write requests -> 401
  # AC2: Authenticated but under-privileged role on write ops -> 403
  # AC3: RBAC matrix - operator/supervisor/administrator can POST/PATCH;
  #      only supervisor/administrator can DELETE
  # AC4: Automated tests cover both 401 and 403 outcomes

  Background:
    Given the inventory API is running with a configured "INVENTORY_API_KEY"

  Rule: Unauthenticated or misauthenticated requests to write endpoints return 401

    Scenario Outline: Missing API key on a write endpoint returns 401
      Given no "X-API-Key" header is supplied
      And no "X-User-Role" header is supplied
      When I send a "<method>" request to "<endpoint>"
      Then the response status is 401

      Examples:
        | method | endpoint                  |
        | POST   | /api/items                |
        | PATCH  | /api/items/{existing_id}  |
        | DELETE | /api/items/{existing_id}  |

    Scenario: Wrong API key value on a write endpoint returns 401
      Given the "X-API-Key" header contains a value that does not match the configured key
      And the "X-User-Role" header is "inventory_operator"
      When I send a "POST" request to "/api/items"
      Then the response status is 401

  Rule: Authenticated requests are subject to role-based access control

    Scenario: Missing role header with a valid API key returns 403
      Given a valid "X-API-Key" header is supplied
      And no "X-User-Role" header is supplied
      When I send a "POST" request to "/api/items"
      Then the response status is 403

    Scenario: Unrecognized role value with a valid API key returns 403
      Given a valid "X-API-Key" header is supplied
      And the "X-User-Role" header is "warehouse_intern"
      When I send a "POST" request to "/api/items"
      Then the response status is 403

    Scenario: Inventory operator attempting DELETE returns 403
      Given a valid "X-API-Key" header is supplied
      And the "X-User-Role" header is "inventory_operator"
      And an inventory item exists
      When I send a "DELETE" request to "/api/items/{existing_id}"
      Then the response status is 403

  Rule: Roles permitted by the RBAC matrix succeed on their allowed write verbs

    Scenario Outline: Allowed role can POST a new item
      Given a valid "X-API-Key" header is supplied
      And the "X-User-Role" header is "<role>"
      When I send a "POST" request to "/api/items" with a unique SKU payload
      Then the response status is 201

      Examples:
        | role                |
        | inventory_operator  |
        | supervisor          |
        | administrator       |

    Scenario Outline: Allowed role can PATCH an existing item
      Given a valid "X-API-Key" header is supplied
      And the "X-User-Role" header is "<role>"
      And an inventory item exists
      When I send a "PATCH" request to "/api/items/{existing_id}" updating the quantity
      Then the response status is 200

      Examples:
        | role                |
        | inventory_operator  |
        | supervisor          |
        | administrator       |

    Scenario Outline: Allowed role can DELETE an existing item
      Given a valid "X-API-Key" header is supplied
      And the "X-User-Role" header is "<role>"
      And an inventory item exists
      When I send a "DELETE" request to "/api/items/{existing_id}"
      Then the response status is 204

      Examples:
        | role          |
        | supervisor    |
        | administrator |

  Rule: Read endpoints remain unauthenticated

    Scenario Outline: Unauthenticated read requests succeed
      Given no "X-API-Key" header is supplied
      And no "X-User-Role" header is supplied
      When I send a "GET" request to "<endpoint>"
      Then the response status is 200

      Examples:
        | endpoint    |
        | /api/items  |
        | /api/health |
