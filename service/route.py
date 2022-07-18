# Copyright 2016, 2019 John J. Rofrano. All Rights Reserved.
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
Suppliers Service

Paths:
------
GET /suppliers - Returns a list all of the Suppliers
GET /suppliers/{id} - Returns the Supplier with a given id number
POST /suppliers - creates a new Supplier record in the database
PUT /suppliers/{id} - updates a Supplier record in the database
DELETE /suppliers/{id} - deletes a Supplier record in the database
"""

from crypt import methods
from unittest import result
from flask import jsonify, request, url_for, abort
from flask.logging import create_logger
from service.model import Supplier, DataValidationError, Item
from . import status  # HTTP Status Codes
from . import app  # Import Flask application

LOG = create_logger(app)

######################################################################
# GET INDEX
######################################################################


@app.route("/")
def index():
    """Root URL response"""
    LOG.info("Request for Root URL")
    return (
        jsonify(
            name="Supplier Demo REST API Service",
            version="1.0",
            paths=url_for("list_suppliers", _external=True),
        ),
        status.HTTP_200_OK,
    )


######################################################################
# LIST ALL SUPPLIERS
######################################################################
@app.route("/suppliers", methods=["GET"])
def list_suppliers():
    """Returns all of the Suppliers"""
    LOG.info("Request for supplier list")
    suppliers = []
    name = request.args.get("name")
    if name:
        suppliers = Supplier.find_by_name(name)
    else:
        suppliers = Supplier.all()

    results = [supplier.serialize() for supplier in suppliers]
    LOG.info("Returning %d suppliers", len(results))
    return jsonify(results), status.HTTP_200_OK


######################################################################
# RETRIEVE A SUPPLIER
######################################################################
@app.route("/suppliers/<int:supplier_id>", methods=["GET"])
def get_suppliers(supplier_id):
    """
    Retrieve a single Supplier

    This endpoint will return a Supplier based on it's id
    """
    LOG.info("Request for supplier with id: %s", supplier_id)
    supplier = Supplier.find(supplier_id)
    if not supplier:
        abort(status.HTTP_404_NOT_FOUND,
              f"Supplier with id '{supplier_id}' was not found.")

    LOG.info("Returning supplier: %s", supplier.name)
    return jsonify(supplier.serialize()), status.HTTP_200_OK


######################################################################
# ADD A NEW SUPPLIER
######################################################################
@app.route("/suppliers", methods=["POST"])
def create_suppliers():
    """
    Creates a Supplier
    This endpoint will create a Supplier based the data in the body that is posted
    """
    try:
        LOG.info("Request to create a supplier")
        check_content_type("application/json")
        supplier = Supplier()
        supplier.deserialize(request.get_json())
        supplier.create()
        message = supplier.serialize()
        location_url = url_for(
            "get_suppliers", supplier_id=supplier.id, _external=True)

        LOG.info("Supplier with ID [%s] created.", supplier.id)
    except DataValidationError as error:
        abort(status.HTTP_400_BAD_REQUEST, str(error))
    return jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}

######################################################################
# UPDATE AN EXISTING SUPPLIER
######################################################################


@app.route("/suppliers/<int:supplier_id>", methods=["PUT"])
def update_suppliers(supplier_id):
    """
    Update a Supplier

    This endpoint will update a Supplier based the body that is posted
    """
    LOG.info("Request to update supplier with id: %s", supplier_id)
    check_content_type("application/json")

    supplier = Supplier.find(supplier_id)
    if not supplier:
        abort(status.HTTP_404_NOT_FOUND,
              f"Supplier with id '{supplier_id}' was not found.")

    supplier.deserialize(request.get_json())
    supplier.id = supplier_id
    supplier.update()

    LOG.info("Supplier with ID [%s] updated.", supplier.id)
    return jsonify(supplier.serialize()), status.HTTP_200_OK


######################################################################
# DELETE A SUPPLIER
######################################################################
@app.route("/suppliers/<int:supplier_id>", methods=["DELETE"])
def delete_suppliers(supplier_id):
    """
    Delete a Supplier

    This endpoint will delete a Supplier based the id specified in the path
    """
    LOG.info("Request to delete supplier with id: %s", supplier_id)
    supplier = Supplier.find(supplier_id)
    if supplier:
        supplier.delete()

    LOG.info("Supplier with ID [%s] delete complete.", supplier_id)
    return "", status.HTTP_204_NO_CONTENT

######################################################################
# ADD A NEW Item
######################################################################


@app.route("/items", methods=["POST"])
def create_items():
    """
    Creates an item
    This endpoint will create an item based the data in the body that is posted
    """
    try:
        LOG.info("Request to create an item")
        check_content_type("application/json")
        item = Item()
        item.deserialize(request.get_json())
        item.create()
        message = item.serialize()
    #location_url = url_for("get_items", item_id=item.id, _external=True)

        LOG.info("Item with ID [%s] created.", item.id)
    except DataValidationError as error:
        abort(status.HTTP_400_BAD_REQUEST, str(error))
    return jsonify(message), status.HTTP_201_CREATED

######################################################################
# LIST ALL ITEMS
######################################################################


@app.route("/items", methods=["GET"])
def list_items():
    """Returns all of the Suppliers"""
    LOG.info("Request for item list")
    items = []
    items = Item.all()

    results = [item.serialize() for item in items]
    LOG.info("Returning %d items", len(results))
    return jsonify(results), status.HTTP_200_OK


######################################################################
# ADD AN ITEM TO A SUPPLIER
######################################################################
@app.route("/suppliers/<int:supplier_id>/items", methods=["POST"])
def add_item_suppliers(supplier_id):
    """
    Add an item to a Supplier

    The endpoint will add an item to a supplier in the relationship table
    """
    LOG.info("Request to add an item to a supplier with id: %s", supplier_id)
    item_id = request.args.get("item_id")
    item = Item.find_by_id(item_id)
    Supplier.create_item_for_supplier(supplier_id=supplier_id, item=item)
    message = {"supplier_id": supplier_id, "item_id": item_id}

    LOG.info("Successfully add an item %s to supplier %s", item_id, supplier_id)
    return jsonify(message), status.HTTP_201_CREATED

######################################################################
# LIST ALL ITEMS OF A SUPPLIER
######################################################################


@app.route("/suppliers/<int:supplier_id>/items", methods=["GET"])
def list_item_suppliers(supplier_id):
    LOG.info("List all items of supplier %s", supplier_id)
    items = []
    items = Supplier.list_items_of_supplier(supplier_id)

    results = [item.serialize() for item in items]
    LOG.info("Returning %d items", len(results))
    return jsonify(results), status.HTTP_200_OK

######################################################################
# DELETE A SUPPLIER
######################################################################


@app.route("/suppliers/<int:supplier_id>/items", methods=["DELETE"])
def delete_item_suppliers(supplier_id):
    LOG.info("Delete an item of supplier %s", supplier_id)
    item_id = request.args.get("item_id")
    item = Item.find_by_id(item_id)

    Supplier.delete_item_for_supplier(supplier_id, item)

    LOG.info(
        "Item with ID [%s] delete for supplier %s complete.", item_id, supplier_id)
    return "", status.HTTP_204_NO_CONTENT

######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################


def check_content_type(media_type):
    """Checks that the media type is correct"""
    content_type = request.headers.get("Content-Type")
    if content_type and content_type == media_type:
        return
    LOG.error("Invalid Content-Type: %s", content_type)
    abort(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        f"Content-Type must be {format(media_type)}",
    )
