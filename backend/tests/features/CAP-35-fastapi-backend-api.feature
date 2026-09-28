@CAP-35 @api @backend @regression
Feature: FastAPI inventory items API
  In order to prevent regressions in the inventory backend
  As a developer
  I want automated tests for health, CRUD, filters and error handling

  Background:
    Given the API is running

  @smoke @critical
  Scenario: Health check returns OK
    When I GET "/health"
    Then the response status should be 200
    And the response JSON should contain:
      | key    | value |
      | status | ok    |

  @critical
  Scenario: Create, read, update and delete an inventory item
    When I create an item with:
      | sku           | name        | category | quantity | reorder_level | location | notes         |
      | CRUD-SKU-1001 | CRUD Widget | Tools    | 5        | 2             | A1       | created by e2e |
    Then the response status should be 201
    And the response JSON should include the created item fields

    When I GET the created item by id
    Then the response status should be 200
    And the item sku should be "CRUD-SKU-1001"

    When I PATCH the created item with:
      | name         | quantity |
      | Updated Name | 10       |
    Then the response status should be 200
    And the item name should be "Updated Name"
    And the item quantity should be 10

    When I DELETE the created item
    Then the response status should be 200

    When I GET the deleted item by id
    Then the response status should be 404

  @regression
  Scenario Outline: Search filter returns items matching sku, name, or category
    Given the inventory contains items:
      | sku           | name       | category |
      | SEARCH-SKU-1  | Magazine   | Media    |
      | OTHER-SKU-2   | Toolbox    | Hardware |
    When I GET "/api/items?search=<search>"
    Then the response status should be 200
    And the response items should contain sku "SEARCH-SKU-1"
    And the response items should not contain sku "OTHER-SKU-2"

    Examples:
      | search |
      | MAGa   |
      | Media  |
      | SKU-1  |

  @regression
  Scenario: Low-stock filter returns only items with quantity less than or equal to reorder level
    Given the inventory contains items:
      | sku          | quantity | reorder_level |
      | LOW-STOCK-1  | 1        | 2             |
      | HIGH-STOCK-2 | 5        | 2             |
    When I GET "/api/items?low_stock=true"
    Then the response status should be 200
    And every response item should satisfy "quantity <= reorder_level"
    And the response items should contain sku "LOW-STOCK-1"
    And the response items should not contain sku "HIGH-STOCK-2"

  @critical
  Scenario: Creating a duplicate SKU returns conflict
    Given an item exists with sku "DUP-SKK-1"
    When I create an item with:
      | sku        | name      | category | quantity | reorder_level | location | notes |
      | DUP-SKK-1  | Duplicate | Test     | 1        | 1             | A1       |       |
    Then the response status should be 409
    And the response JSON should equal:
      | key    | value              |
      | detail | SKU already exists |

  @critical
  Scenario: Updating a missing item returns not found
    When I PATCH "/api/items/999999" with JSON:
      | key  | value    |
      | name | Not here |
    Then the response status should be 404
    And the response JSON should equal:
      | key    | value          |
      | detail | Item not found |

  @critical
  Scenario: Deleting a missing item returns not found
    When I DELETE "/api/items/999999"
    Then the response status should be 404
    And the response JSON should equal:
      | key    | value          |
      | detail | Item not found |
