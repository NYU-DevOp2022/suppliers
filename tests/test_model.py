# Copyright 2016, 2021 John J. Rofrano. All Rights Reserved.
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
Test cases for supplier Model

Test cases can be run with:
    nosetests
    coverage report -m

While debugging just these tests it's convenient to use this:
    nosetests --stop tests/test_suppliers.py:TestSupplierModel

"""
# from itertools import product
import os
import logging
import unittest
# from datetime import date
from werkzeug.exceptions import NotFound
from service.model import Item, Supplier, DataValidationError, db
from service import app
from tests.factories import ItemFactory, SupplierFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/testdb"
)


######################################################################
#  P E T   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestSupplierModel(unittest.TestCase):
    """Test Cases for Supplier Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Supplier.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Supplier).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################
    def test_create_a_supplier(self):
        """It should Create a supplier and assert that it exists"""
        supplier = Supplier(name="Amazon", available=True,
                            address="NY", rating=4.7)
        self.assertEqual(str(supplier), "<Supplier 'Amazon' id=[None]>")
        self.assertTrue(supplier is not None)
        self.assertEqual(supplier.id, None)
        self.assertEqual(supplier.name, "Amazon")
        self.assertEqual(supplier.available, True)
        self.assertEqual(supplier.address, "NY")
        self.assertEqual(supplier.rating, 4.7)
        supplier = Supplier(name="Amazon", available=False,
                            address="NJ", rating=4.5)
        self.assertEqual(supplier.available, False)
        self.assertEqual(supplier.address, "NJ")
        self.assertEqual(supplier.rating, 4.5)

    def test_add_a_supplier(self):
        """It should Create a supplier and add it to the database"""
        suppliers = Supplier.all()
        self.assertEqual(suppliers, [])
        supplier = Supplier(name="Amazon", available=True,
                            address="NY", rating=4.7)
        self.assertTrue(supplier is not None)
        self.assertEqual(supplier.id, None)
        supplier.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(supplier.id)
        suppliers = supplier.all()
        self.assertEqual(len(suppliers), 1)

    def test_read_a_supplier(self):
        """It should Read a Supplier"""
        supplier = SupplierFactory()
        logging.debug(supplier)
        supplier.id = None
        supplier.create()
        self.assertIsNotNone(supplier.id)
        # Fetch it back
        found_supplier = Supplier.find(supplier.id)
        self.assertEqual(found_supplier.id, supplier.id)
        self.assertEqual(found_supplier.name, supplier.name)
        self.assertEqual(found_supplier.address, supplier.address)
        self.assertEqual(found_supplier.rating, supplier.rating)

    def test_update_a_supplier(self):
        """It should Update a Supplier"""
        supplier = SupplierFactory()
        logging.debug(supplier)
        supplier.id = None
        supplier.create()
        logging.debug(supplier)
        self.assertIsNotNone(supplier.id)
        # Change it an save it
        supplier.products = 12138
        original_id = supplier.id
        supplier.update()
        self.assertEqual(supplier.id, original_id)
        self.assertEqual(supplier.products, 12138)
        # Fetch it back and make sure the id hasn't changed
        # but the data did change
        suppliers = Supplier.all()
        self.assertEqual(len(suppliers), 1)
        self.assertEqual(suppliers[0].id, original_id)
        self.assertEqual(suppliers[0].products, 12138)

    def test_update_no_id(self):
        """It should not Update a Supplier with no id"""
        supplier = SupplierFactory()
        logging.debug(supplier)
        supplier.id = None
        self.assertRaises(DataValidationError, supplier.update)

    def test_delete_a_supplier(self):
        """It should Delete a Supplier"""
        supplier = SupplierFactory()
        supplier.create()
        self.assertEqual(len(Supplier.all()), 1)
        # delete the supplier and make sure it isn't in the database
        supplier.delete()
        self.assertEqual(len(Supplier.all()), 0)

    def test_list_all_suppliers(self):
        """It should List all Suppliers in the database"""
        suppliers = Supplier.all()
        self.assertEqual(suppliers, [])
        # Create 5 Suppliers
        for i in range(5):
            supplier = SupplierFactory()
            supplier.create()
        # See if we get back 5 suppliers
        suppliers = Supplier.all()
        self.assertEqual(len(suppliers), 5)

    def test_find_all_suppliers_by_rating(self):
        """It should List all Suppliers in the database based on rating"""
        suppliers = Supplier.all()
        self.assertEqual(suppliers, [])
        s_empty = Supplier.all()
        self.assertEqual(s_empty, [])
        # Create 5 Suppliers with rating 5.0
        for i in range(10):
            supplier = SupplierFactory()
            supplier.create()
            supplier.rating = 5.0
        # See if we get all the suppliers
        suppliers = Supplier.find_by_rating(5.0)
        suppliers = [supplier.serialize() for supplier in suppliers]
        s_empty = Supplier.find_by_rating(6.0)
        s_empty = [supplier.serialize() for supplier in s_empty]
        self.assertEqual(len(suppliers), 10)
        self.assertEqual(len(s_empty), 0)

    def test_serialize_a_supplier(self):
        """It should serialize a Supplier"""
        supplier = SupplierFactory()
        data = supplier.serialize()
        self.assertNotEqual(data, None)
        self.assertIn("id", data)
        self.assertEqual(data["id"], supplier.id)
        self.assertIn("name", data)
        self.assertEqual(data["name"], supplier.name)
        self.assertIn("address", data)
        self.assertEqual(data["address"], supplier.address)
        self.assertIn("rating", data)
        self.assertEqual(data["rating"], supplier.rating)
        self.assertIn("available", data)
        self.assertEqual(data["available"], supplier.available)

    def test_deserialize_a_supplier(self):
        """It should de-serialize a Supplier"""
        data = SupplierFactory().serialize()
        supplier = Supplier()
        supplier.deserialize(data)
        self.assertNotEqual(supplier, None)
        self.assertEqual(supplier.id, None)
        self.assertNotEqual(supplier.name, 1)
        self.assertEqual(supplier.name, data["name"])
        self.assertEqual(supplier.address, data["address"])
        self.assertEqual(supplier.rating, data["rating"])
        self.assertEqual(supplier.available, data["available"])

    def test_deserialize_missing_data(self):
        """It should not deserialize a Supplier with missing data"""
        data = {"id": 1, "name": "Kitty", "category": "cat"}
        supplier = Supplier()
        self.assertRaises(DataValidationError, supplier.deserialize, data)

    def test_deserialize_bad_data(self):
        """It should not deserialize bad data"""
        data = "this is not a dictionary"
        supplier = Supplier()
        self.assertRaises(DataValidationError, supplier.deserialize, data)

    def test_deserialize_bad_available(self):
        """It should not deserialize a bad available attribute"""
        test_supplier = SupplierFactory()
        data = test_supplier.serialize()
        # Here replace boolean attribute with a string value, type mismatch
        data["available"] = "true"
        supplier = Supplier()
        self.assertRaises(DataValidationError, supplier.deserialize, data)

    def test_deserialize_bad_name(self):
        """It should not serialize a bad products attribute"""
        test_supplier = SupplierFactory()
        data = test_supplier.serialize()
        data["name"] = 123  # wrong case
        supplier = Supplier()
        self.assertRaises(DataValidationError, supplier.deserialize, data)

    def test_deserialize_bad_address(self):
        """It should not serialize a bad products attribute"""
        test_supplier = SupplierFactory()
        data = test_supplier.serialize()
        data["address"] = 123
        supplier = Supplier()
        self.assertRaises(DataValidationError, supplier.deserialize, data)

    # def test_deserialize_bad_rating(self):
    #     """It should not serialize a bad products attribute"""
    #     test_supplier = SupplierFactory()
    #     data = test_supplier.serialize()
    #     data["rating"] = "111"
    #     supplier = Supplier()
    #     self.assertRaises(DataValidationError, supplier.deserialize, data)

    def test_find_supplier(self):
        """It should Find a Supplier by ID"""
        suppliers = SupplierFactory.create_batch(5)
        for supplier in suppliers:
            supplier.create()
        logging.debug(suppliers)
        # make sure they got saved
        self.assertEqual(len(Supplier.all()), 5)
        # find the 2nd supplier in the list
        supplier = Supplier.find(suppliers[1].id)
        self.assertIsNot(supplier, None)
        self.assertEqual(supplier.id, suppliers[1].id)
        self.assertEqual(supplier.name, suppliers[1].name)
        self.assertEqual(supplier.available, suppliers[1].available)
        self.assertEqual(supplier.address, suppliers[1].address)
        self.assertEqual(supplier.rating, suppliers[1].rating)

    def test_find_by_name(self):
        """It should Find a Supplier by Name"""
        suppliers = SupplierFactory.create_batch(5)
        for supplier in suppliers:
            supplier.create()
        name = suppliers[0].name
        count = len([x for x in suppliers if x.name == name])
        found = Supplier.find_by_name(name)
        self.assertEqual(found.count(), count)
        self.assertEqual(found[0].address, suppliers[0].address)
        self.assertEqual(found[0].rating, suppliers[0].rating)
        self.assertEqual(found[0].name, suppliers[0].name)
        self.assertEqual(found[0].available, suppliers[0].available)

    def test_find_by_address(self):
        """It should Find a Supplier by Address"""
        suppliers = SupplierFactory.create_batch(5)
        for supplier in suppliers:
            supplier.create()
        address = suppliers[0].address

        found = Supplier.find_by_address(address)
        self.assertEqual(found.count(), 1)
        self.assertEqual(found[0].address, suppliers[0].address)
        self.assertEqual(found[0].rating, suppliers[0].rating)
        self.assertEqual(found[0].name, suppliers[0].name)
        self.assertEqual(found[0].available, suppliers[0].available)

        found = Supplier.find_by_address("Invalid address!")
        self.assertEqual(found.count(), 0)

    def test_find_by_availability(self):
        """It should Find Suppliers by Availability"""
        suppliers = SupplierFactory.create_batch(10)
        for supplier in suppliers:
            supplier.create()
        available = suppliers[0].available
        count = len(
            [supplier for supplier in suppliers if supplier.available == available])
        found = Supplier.find_by_availability(available)
        self.assertEqual(found.count(), count)
        for supplier in found:
            self.assertEqual(supplier.available, available)

    def test_find_or_404_found(self):
        """It should Find or return 404 not found"""
        suppliers = SupplierFactory.create_batch(3)
        for supplier in suppliers:
            supplier.create()
        supplier = Supplier.find_or_404(suppliers[1].id)
        self.assertIsNot(supplier, None)
        self.assertEqual(supplier.id, suppliers[1].id)
        self.assertEqual(supplier.name, suppliers[1].name)
        self.assertEqual(supplier.available, suppliers[1].available)
        self.assertEqual(supplier.address, suppliers[1].address)
        self.assertEqual(supplier.rating, suppliers[1].rating)

    def test_find_or_404_not_found(self):
        """It should return 404 not found"""
        self.assertRaises(NotFound, Supplier.find_or_404, 0)

    def test_create_an_item(self):
        """It should Create an item and assert that it exists"""
        item = Item(name="ps5")
        self.assertEqual(str(item), "<Item 'ps5' id=[None]>")
        self.assertTrue(item is not None)
        self.assertEqual(item.id, None)
        self.assertEqual(item.name, "ps5")

    def test_add_an_item(self):
        """It should Create an item and add it to the database"""
        items = Item.all()
        self.assertEqual(items, [])
        item = Item(name="ps5")
        self.assertTrue(item is not None)
        self.assertEqual(item.id, None)
        item.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(item.id)
        items = item.all()
        self.assertEqual(len(items), 1)

    def test_serialize_an_item(self):
        """It should serialize a Supplier"""
        item = ItemFactory()
        data = item.serialize()
        self.assertNotEqual(data, None)
        self.assertIn("id", data)
        self.assertEqual(data["id"], item.id)
        self.assertIn("name", data)
        self.assertEqual(data["name"], item.name)

    def test_deserialize_bad_item_name(self):
        """It should not deserialize a bad available attribute"""
        test_item = ItemFactory()
        data = test_item.serialize()
        # Here replace boolean attribute with a string value, type mismatch
        data["name"] = 123
        item = Item()
        self.assertRaises(DataValidationError, item.deserialize, data)

    def test_deserialize_an_item(self):
        """It should de-serialize a Supplier"""
        data = ItemFactory().serialize()
        item = Item()
        item.deserialize(data)
        self.assertNotEqual(item, None)
        self.assertEqual(item.id, None)
        self.assertNotEqual(item.name, 1)
        self.assertEqual(item.name, data["name"])

    def test_deserialize_missing_data_item(self):
        """It should not deserialize an Item with missing data"""
        data = {"id": 1}
        item = Item()
        self.assertRaises(DataValidationError, item.deserialize, data)

    def test_deserialize_bad_data_item(self):
        """It should not deserialize bad data"""
        data = "this is not a dictionary"
        item = Item()
        self.assertRaises(DataValidationError, item.deserialize, data)

    def test_find_by_item_id(self):
        """It should Find an Item by id"""
        items = ItemFactory.create_batch(5)
        for item in items:
            item.create()
        id = items[0].id
        found = Item.find_by_id(id)
        self.assertEqual(found.name, items[0].name)

    def test_find_item_by_name(self):
        """It should Find a Supplier by Name"""
        idx = [0, 2, 3]
        items = ItemFactory.create_batch(5)
        for i in idx:
            items[i].name = "Iphone13"

        for item in items:
            item.create()
        name = items[0].name
        found = Item.find_by_name(name)
        self.assertEqual(found.count(), 3)
        for i in range(3):
            self.assertEqual(found[i].id, items[idx[i]].id)
            self.assertEqual(found[i].name, "Iphone13")

    def test_list_item_for_supplier(self):
        """It should List items for Supplier"""
        supplier = SupplierFactory()
        supplier.create()
        id = supplier.id
        logging.debug(supplier)
        items_of_supplier = Supplier.list_items_of_supplier(id)
        self.assertEqual(items_of_supplier, [])

        items = ItemFactory.create_batch(5)
        for item in items:
            item.create()
            Supplier.create_item_for_supplier(id, item)
        logging.debug(items)
        items_of_supplier = Supplier.list_items_of_supplier(id)
        self.assertEqual(len(items_of_supplier), 5)
        self.assertEqual(items_of_supplier[3].name, items[3].name)

    def test_create_item_for_supplier(self):
        """It should Create items for Supplier"""
        supplier = SupplierFactory()
        supplier.create()
        id = supplier.id
        logging.debug(supplier)

        items = ItemFactory.create_batch(3)
        for item in items:
            item.create()
            Supplier.create_item_for_supplier(id, item)
        logging.debug(items)

        items_of_supplier = Supplier.list_items_of_supplier(id)
        self.assertEqual(len(items_of_supplier), 3)
        self.assertEqual(items_of_supplier[0].name, items[0].name)

    def test_delete_item_for_supplier(self):
        """It should Delete items for Supplier"""
        supplier = SupplierFactory()
        supplier.create()
        id = supplier.id
        logging.debug(supplier)

        items = ItemFactory.create_batch(5)
        for item in items:
            item.create()
            Supplier.create_item_for_supplier(id, item)
        logging.debug(items)
        items_of_supplier = Supplier.list_items_of_supplier(id)
        self.assertEqual(len(items_of_supplier), 5)
        self.assertEqual(items_of_supplier[0].name, items[0].name)

        Supplier.delete_item_for_supplier(id, items[1])
        Supplier.delete_item_for_supplier(id, items[2])
        items_of_supplier = Supplier.list_items_of_supplier(id)
        self.assertEqual(len(items_of_supplier), 3)
        self.assertEqual(items_of_supplier[0].name, items[0].name)
        self.assertEqual(items_of_supplier[1].name, items[3].name)

    def test_list_suppliers_for_item(self):
        """It should List Suppliers for Item"""
        item = ItemFactory()
        item.create()
        id = item.id
        logging.debug(item)
        suppliers_of_item = Item.list_suppliers_of_item(id)
        self.assertEqual(suppliers_of_item, [])

        suppliers = SupplierFactory.create_batch(5)
        for supplier in suppliers:
            supplier.create()
            Supplier.create_item_for_supplier(supplier.id, item)
        suppliers_of_item = Item.list_suppliers_of_item(id)
        self.assertEqual(len(suppliers_of_item), 5)
        self.assertEqual(suppliers_of_item[3].name, suppliers[3].name)
