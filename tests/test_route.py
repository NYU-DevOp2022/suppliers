# Copyright 2016, 2022 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Supplier API Service Test Suite

Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
  codecov --token=$CODECOV_TOKEN

  While debugging just these tests it's convenient to use this:
    nosetests --stop tests/test_service.py:TestSupplierService
"""

import os
import logging
import unittest
import json

# from unittest.mock import MagicMock, patch
# from urllib.parse import quote_plus
from service import app, status
from service.model import db, init_db, Supplier, DataValidationError
from tests.factories import ItemFactory, SupplierFactory
from unittest.mock import patch

# Disable all but critical errors during normal test run
# uncomment for debugging failing tests
# logging.disable(logging.CRITICAL)

# DATABASE_URI = os.getenv('DATABASE_URI', 'sqlite:///../db/test.db')
DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/testdb"
)
BASE_URL = "/suppliers"
ITEM_URL = "/items"
CONTENT_TYPE_JSON = "application/json"


######################################################################
#  T E S T   S U P P L I E R   S E R V I C E
######################################################################
class TestSupplierService(unittest.TestCase):
    """Supplier Server Tests"""

    @classmethod
    def setUpClass(cls):
        """Run once before all tests"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        # Set up the test database
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        init_db(app)

    @classmethod
    def tearDownClass(cls):
        """Run once after all tests"""
        db.session.close()

    def setUp(self):
        """Runs before each test"""
        self.client = app.test_client()
        db.session.query(Supplier).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        db.session.remove()

    def _create_suppliers(self, count):
        """Factory method to create suppliers in bulk"""
        suppliers = []
        for _ in range(count):
            test_supplier = SupplierFactory()
            response = self.client.post(
                BASE_URL, json=test_supplier.serialize(), content_type=CONTENT_TYPE_JSON
            )
            self.assertEqual(
                response.status_code, status.HTTP_201_CREATED, "Could not create test supplier"
            )
            new_supplier = response.get_json()
            test_supplier.id = new_supplier["id"]
            suppliers.append(test_supplier)
        return suppliers

    def _create_items(self, count):
        items = []
        for _ in range(count):
            test_item = ItemFactory()
            response = self.client.post(
                ITEM_URL, json=test_item.serialize(), content_type=CONTENT_TYPE_JSON
            )
            self.assertEqual(
                response.status_code, status.HTTP_201_CREATED, "Could not create test item"
            )
            new_item = response.get_json()
            test_item.id = new_item["id"]
            items.append(test_item)
        return items

    def _create_suppliers_rating(self, count, rating):
        """Factory method to create suppliers in bulk"""
        suppliers = []
        for _ in range(count):
            test_supplier = SupplierFactory()
            test_supplier.rating = rating
            response = self.client.post(
                BASE_URL, json=test_supplier.serialize(), content_type=CONTENT_TYPE_JSON
            )
            self.assertEqual(
                response.status_code, status.HTTP_201_CREATED, "Could not create test supplier"
            )
            new_supplier = response.get_json()
            test_supplier.id = new_supplier["id"]
            suppliers.append(test_supplier)
        return suppliers

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################


    def test_index(self):
        """It should call the Home Page"""
        response = self.client.get("/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data["name"], "Supplier Demo REST API Service")

    def test_get_supplier_list(self):
        """It should Get a list of Suppliers"""
        self._create_suppliers(5)
        response = self.client.get(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 5)

    def test_get_supplier(self):
        """It should Get a single Supplier"""
        # get the id of a supplier
        test_supplier = self._create_suppliers(1)[0]
        response = self.client.get(f"{BASE_URL}/{test_supplier.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data["name"], test_supplier.name)

    def test_get_suppliers_by_rating(self):
        """It should Get all Suppliers based on rating"""
        # get the id of the suppliers
        test_supplier = self._create_suppliers_rating(5, 5.0)[0]
        all = self.client.get(BASE_URL)
        self.assertEqual(all.status_code, status.HTTP_200_OK)
        alldata = all.get_json()
        self.assertEqual(len(alldata), 5)
        response = self.client.get(f"{BASE_URL}/rating/{test_supplier.rating}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(test_supplier.rating, 5.0)
        self.assertEqual(len(data), 5)
        self.assertEqual(data[0]["rating"], 5.0)

    def test_get_supplier_not_found(self):
        """It should not Get a Supplier thats not found"""
        response = self.client.get(f"{BASE_URL}/0")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data = response.get_json()
        logging.debug("Response data = %s", data)
        self.assertIn("was not found", data["message"])

    def test_create_supplier(self):
        """It should Create a new supplier"""
        test_supplier = SupplierFactory()
        logging.debug("Test Supplier: %s", test_supplier.serialize())
        response = self.client.post(
            BASE_URL,
            json=test_supplier.serialize(),
            content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Make sure location header is set
        location = response.headers.get("Location", None)
        self.assertIsNotNone(location)

        # Check the data is correct
        new_supplier = response.get_json()
        self.assertEqual(new_supplier["name"], test_supplier.name)
        self.assertEqual(new_supplier["available"], test_supplier.available)
        self.assertEqual(new_supplier["address"], test_supplier.address)
        self.assertEqual(new_supplier["rating"], test_supplier.rating)

        # Check that the location header was correct   ???
        response = self.client.get(location, content_type=CONTENT_TYPE_JSON)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        new_supplier = response.get_json()
        self.assertEqual(new_supplier["name"], test_supplier.name)
        self.assertEqual(new_supplier["available"], test_supplier.available)
        self.assertEqual(new_supplier["address"], test_supplier.address)
        self.assertEqual(new_supplier["rating"], test_supplier.rating)

    def test_update_bad_supplier(self):
        NotFoundResponse = self.client.get(f"{BASE_URL}/0")
        self.assertEqual(NotFoundResponse.status_code,
                         status.HTTP_404_NOT_FOUND)

    def test_update_supplier(self):
        """It should Update an existing supplier"""
        # create a supplier to update
        test_supplier = SupplierFactory()
        response = self.client.post(
            BASE_URL,
            json=test_supplier.serialize(),
            content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # update the supplier
        new_supplier = response.get_json()
        logging.debug(new_supplier)
        new_supplier["address"] = "NY"

        response = self.client.put(
            f"{BASE_URL}/{new_supplier['id']}",
            json=new_supplier,
            content_type=CONTENT_TYPE_JSON,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        updated_supplier = response.get_json()
        self.assertEqual(updated_supplier["address"], "NY")

    def test_delete_supplier(self):
        """It should Delete a supplier"""
        test_supplier = self._create_suppliers(1)[0]
        response = self.client.delete(f"{BASE_URL}/{test_supplier.id}")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(response.data), 0)
        # make sure they are deleted
        response = self.client.get(f"{BASE_URL}/{test_supplier.id}")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_item(self):
        """It should Create a new item"""
        test_item = ItemFactory()
        logging.debug("Test Item: %s", test_item.serialize())
        response = self.client.post(
            ITEM_URL,
            json=test_item.serialize(),
            content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Check the data is correct
        new_item = response.get_json()
        self.assertEqual(new_item["name"], test_item.name)

    def test_delete_item(self):
        """It should Delete an item"""
        test_item = self._create_items(1)[0]
        response = self.client.delete(f"{ITEM_URL}/{test_item.id}")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(response.data), 0)

    def test_get_item_list(self):
        """It should Get a list of Items"""
        self._create_items(5)
        response = self.client.get(ITEM_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_add_item_suppliers(self):
        test_supplier = self._create_suppliers(1)[0]
        test_item = self._create_items(1)[0]

        test_dict = {"supplier_id": test_supplier.id, "item_id": test_item.id}
        test_json = json.dumps(test_dict)

        response = self.client.post(
            f"{BASE_URL}/{test_supplier.id}/items?item_id={test_item.id}",
            json=test_json,
            content_type=CONTENT_TYPE_JSON
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_list_item_suppliers(self):

        test_supplier = self._create_suppliers(1)[0]
        test_item = self._create_items(1)[0]

        test_dict = {"supplier_id": test_supplier.id, "item_id": test_item.id}
        test_json = json.dumps(test_dict)

        response = self.client.post(
            f"{BASE_URL}/{test_supplier.id}/items?item_id={test_item.id}",
            json=test_json,
            content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.get(f"{BASE_URL}/{test_supplier.id}/items")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_item_suppliers(self):

        test_supplier = self._create_suppliers(1)[0]
        test_item = self._create_items(1)[0]

        test_dict = {"supplier_id": test_supplier.id, "item_id": test_item.id}
        test_json = json.dumps(test_dict)

        response = self.client.post(
            f"{BASE_URL}/{test_supplier.id}/items?item_id={test_item.id}",
            json=test_json,
            content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.delete(
            f"{BASE_URL}/{test_supplier.id}/items?item_id={test_item.id}")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(response.data), 0)

    # TO DO: Need to modify route.py to complement this test.
    # def test_query_supplier_list_by_products(self):
    #     """It should Query suppliers by Products"""
    #     suppliers = self._create_suppliers(10)
    #     test_products = suppliers[0].products
    #     products_suppliers = [supplier for supplier in suppliers if supplier.products == test_products]
    #     response = self.client.get(
    #         BASE_URL,
    #         query_string=f"products={quote_plus(str(test_products))}"
    #     )
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     data = response.get_json()
    #     self.assertEqual(len(data), len(products_suppliers))
    #     # check the data just to be sure
    #     for supplier in data:
    #         self.assertEqual(supplier["products"], test_products)

    ######################################################################
    #  T E S T   S A D   P A T H S
    ######################################################################

    def test_create_supplier_no_data(self):
        """It should not Create a supplier with missing data"""
        response = self.client.post(
            BASE_URL,
            json={},
            content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_supplier_no_content_type(self):
        """It should not Create a supplier with no content type"""
        response = self.client.post(BASE_URL)
        self.assertEqual(response.status_code,
                         status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_create_supplier_bad_available(self):
        """It should not Create a supplier with bad available data"""
        test_supplier = SupplierFactory()
        logging.debug(test_supplier)
        # change available to a string
        test_supplier.available = "true"
        response = self.client.post(
            BASE_URL,
            json=test_supplier.serialize(),
            content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_supplier_bad_id(self):
        """It should not find an existing supplier"""
        # create a supplier to update
        test_supplier = SupplierFactory()

        response = self.client.post(
            BASE_URL,
            json=test_supplier.serialize(),
            content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # update the supplier
        new_supplier = response.get_json()
        logging.debug(new_supplier)
        new_supplier["id"] = 10086

        response = self.client.put(
            f"{BASE_URL}/{new_supplier['id']}",
            json=new_supplier,
            content_type=CONTENT_TYPE_JSON,
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_item_no_data(self):
        """It should not Create an item with missing data"""
        response = self.client.post(
            ITEM_URL,
            json={},
            content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    ######################################################################
    #  T E S T   M O C K S
    ######################################################################

    # TO DO: "Keyword 'patch' not find error" need to be figure out.
    @patch('service.route.Supplier.find_by_name')
    def test_bad_request(self, bad_request_mock):
        """It should return a Bad Request error from Find By Name"""
        bad_request_mock.side_effect = DataValidationError()
        response = self.client.get(BASE_URL, query_string='name=fido')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # @patch('service.route.Supplier.find_by_name')
    # def test_mock_search_data(self, supplier_find_mock):
    #     """It should showing how to mock data"""
    #     supplier_find_mock.return_value = [MagicMock(serialize=lambda: {'name': 'fido'})]
    #     response = self.client.get(BASE_URL, query_string='name=fido')
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
