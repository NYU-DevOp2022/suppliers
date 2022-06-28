# Copyright 2016, 2021 John Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Models for suppliers Demo Service

All of the models are stored in this module

Models
------
Supplier -- A Supplier

Attributes:
-----------
id(int) - the id of the supplier
name (string) - the name of the supplier
available (boolean) - indicate whether the supplier is active or not
products (list of int) - a list of product id provided by the supplier
"""
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

logger = logging.getLogger("flask.app")

# Create the SQLAlchemy object to be initialized later in init_db()
# pylint: disable=no-member
db = SQLAlchemy()


def init_db(app):
    """Initialize the SQLAlchemy app"""
    Supplier.init_db(app)


class DataValidationError(Exception):
    """Used for an data validation errors when deserializing"""


class Supplier(db.Model):
    """
    Class that represents a Supplier

    This version uses a relational database for persistence which is hidden
    from us by SQLAlchemy's object relational mappings (ORM)
    """

    ##################################################
    # Table Schema
    ##################################################
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(63), nullable=False)
    available = db.Column(db.Boolean(), nullable=False, default=False)
    products = db.Column(db.Integer, nullable=True)

    ##################################################
    # INSTANCE METHODS
    ##################################################

    def __repr__(self):
        return f"<Supplier '{self.name}' id=[{self.id}]>"

    def create(self):
        """
        Creates a Supplier to the database
        """
        logger.info("Creating %s", self.name)
        # id must be none to generate next primary key
        self.id = None  # pylint: disable=invalid-name
        db.session.add(self)
        db.session.commit()

    def update(self):
        """
        Updates a Supplier to the database
        """
        logger.info("Saving %s", self.name)
        if not self.id:
            raise DataValidationError("Update called with empty ID field")
        db.session.commit()

    def delete(self):
        """Removes a Supplier from the data store"""
        logger.info("Deleting %s", self.name)
        db.session.delete(self)
        db.session.commit()

    def serialize(self) -> dict:
        """Serializes a Supplier into a dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "products": self.products,
            "available": self.available,
        }

    def deserialize(self, data: dict):
        """
        Deserializes a Supplier from a dictionary
        Args:
            data (dict): A dictionary containing the Supplier data
        """
        try:
            if isinstance(data["name"], str):
                self.name = data["name"]
            else:
                raise DataValidationError(
                    "Invalid type for str [name]: " + str(type(data["name"]))
                )
            if isinstance(data["available"], bool):
                self.available = data["available"]
            else:
                raise DataValidationError(
                    "Invalid type for boolean [available]: " + str(type(data["available"]))
                )

            if isinstance(data["products"], int):
                if data["products"] >= 0:
                    self.products = data["products"]
                else:
                    raise DataValidationError(
                        "Invalid value for [products]: " + str(type(data["products"]))
                    )
            else:
                raise DataValidationError(
                    "Invalid type for integer [products]: " + str(type(data["products"]))
                )

        except KeyError as error:
            raise DataValidationError("Invalid supplier: missing " + error.args[0]) from error
        except TypeError as error:
            raise DataValidationError(
                "Invalid supplier: body of request contained bad or no data " + str(error)
            ) from error
        return self

    ##################################################
    # CLASS METHODS
    ##################################################

    @classmethod
    def init_db(cls, app: Flask):
        """Initializes the database session

        :param app: the Flask app
        :type data: Flask

        """
        logger.info("Initializing database")
        # This is where we initialize SQLAlchemy from the Flask app
        db.init_app(app)
        app.app_context().push()
        db.create_all()  # make our sqlalchemy tables

    @classmethod
    def all(cls) -> list:
        """Returns all of the Suppliers in the database"""
        logger.info("Processing all Suppliers")
        return cls.query.all()

    @classmethod
    def find(cls, supplier_id: int):
        """Finds a supplier by it's ID

        :param supplier_id: the id of the Supplier to find
        :type supplier_id: int

        :return: an instance with the supplier_id, or None if not found
        :rtype: Supplier

        """
        logger.info("Processing lookup for id %s ...", supplier_id)
        return cls.query.get(supplier_id)

    @classmethod
    def find_or_404(cls, supplier_id: int):
        """Find a supplier by it's id

        :param supplier_id: the id of the Supplier to find
        :type supplier_id: int

        :return: an instance with the supplier_id, or 404_NOT_FOUND if not found
        :rtype: Supplier

        """
        logger.info("Processing lookup or 404 for id %s ...", supplier_id)
        return cls.query.get_or_404(supplier_id)

    @classmethod
    def find_by_name(cls, name: str) -> list:
        """Returns all Suppliers with the given name

        :param name: the name of the Suppliers you want to match
        :type name: str

        :return: a collection of Suppliers with that name
        :rtype: list

        """
        logger.info("Processing name query for %s ...", name)
        return cls.query.filter(cls.name == name)

    @classmethod
    def find_by_products(cls, products: int) -> list:
        """Returns all of the suppliers in a category

        :param category: the category of the suppliers you want to match
        :type category: str

        :return: a collection of suppliers in that category
        :rtype: list

        """
        logger.info("Processing products query for %s ...", products)
        return cls.query.filter(cls.products == products)

    @classmethod
    def find_by_availability(cls, available: bool = True) -> list:
        """Returns all Suppliers by their availability

        :param available: True for suppliers that are available
        :type available: str

        :return: a collection of Suppliers that are available
        :rtype: list

        """
        logger.info("Processing available query for %s ...", available)
        return cls.query.filter(cls.available == available)
