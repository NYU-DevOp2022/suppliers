Feature: The supplier store service back-end
    As a manager
    I need a RESTful catalog service
    So that I can keep track of all the suppliers

Background:
    Given the following suppliers
        | name       | available | address  | rating     |
        | Jack       | True      | NJ       | 4.8        |
        | Tony       | True      | NY       | 4.9        |
        | Tom        | False     | CA       | 4.5        |
        | Frank      | True      | NY       | 4.6        |


Scenario: The server is running
    When I visit the "Home Page"
    Then I should see "NYU Devops suppliers" in the title
    And I should not see "404 Not Found"

Scenario: Page Route
    When I visit the "Home Page"
    And I press the "Items" button
    Then I should see "NYU Devops items" in the title
    

Scenario: Create a Supplier
    When I visit the "Home Page"
    And I set the "Name" to "Amy"
    And I select "False" in the "Available" dropdown
    And I set the "Address" to "NY"
    And I set the "Rating" to "4.5"
    And I press the "Create" button
    Then I should see the message "Success"
    When I copy the "Id" field
    And I press the "Clear" button
    Then the "Id" field should be empty
    And the "Name" field should be empty
    And the "Address" field should be empty
    And the "Rating" field should be empty
    When I paste the "Id" field
    And I press the "Retrieve" button
    Then I should see the message "Success"
    And I should see "Amy" in the "Name" field
    And I should see "False" in the "Available" dropdown
    And I should see "NY" in the "Address" field
    And I should see "4.5" in the "Rating" field

Scenario: List all suppliers
    When I visit the "Home Page"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "Jack" in the results
    And I should see "Tony" in the results
    And I should not see "Tom" in the results

Scenario: Search for suppliers
    When I visit the "Home Page"
    And I press the "Clear" button
    And I set the "Address" to "NY"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "Tony" in the results
    And I should see "Frank" in the results    
    And I should not see "Jack" in the results
    And I should not see "Tom" in the results

Scenario: Search for available
    When I visit the "Home Page"
    And I press the "Clear" button
    And I select "True" in the "Available" dropdown
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "Jack" in the results
    And I should see "Tony" in the results
    And I should see "Frank" in the results
    And I should not see "Tom" in the results

Scenario: Update a Supplier
    When I visit the "Home Page"
    And I set the "Name" to "Tony"
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "Tony" in the "Name" field
    And I should see "NY" in the "Address" field
    When I change "Name" to "Dongzhe"
    And I press the "Update" button
    Then I should see the message "Success"
    When I copy the "Id" field
    And I press the "Clear" button
    And I paste the "Id" field
    And I press the "Retrieve" button
    Then I should see the message "Success"
    And I should see "Dongzhe" in the "Name" field
    When I press the "Clear" button
    And I press the "Search" button
    Then I should see the message "Success"
    And I should see "Dongzhe" in the results
    And I should not see "Tony" in the results

Scenario: Create a Item
    When I visit the "Home Page"
    And I press the "Items" button
    And I set the "Name" to "Coat" in the item field
    And I press the "Create" button in the item field
    Then I should see the message "Success" in the item field
    When I copy the "Id" in the item field
    And I press the "Clear" button in the item field
    Then the "Id" in the item field should be empty
    And the "Name" in the item field should be empty


Scenario: Search for items
    When I visit the "Home Page"
    And I press the "Items" button
    And I press the "Clear" button in the item field
    And I set the "Name" to "Ipad" in the item field
    And I press the "Search" button in the item field
    Then I should see the message "Success" in the item field
    Then I should see "Ipad" in the results in the item field


Scenario: Delete a item
    When I visit the "Home Page"
    And I press the "Items" button
    And I set the "Name" to "Coat" in the item field
    And I press the "Create" button in the item field
    Then I should see the message "Success" in the item field
    When I copy the "Id" in the item field
    And I press the "Clear" button in the item field
    Then the "Id" in the item field should be empty
    And the "Name" in the item field should be empty
    When I paste the "Id" in the item field
    And I press the "Delete" button in the item field
    Then I should see the message "Item has been Deleted!" in the item field