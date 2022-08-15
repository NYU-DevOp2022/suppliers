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

import secrets
from functools import wraps
from flask_restx import Resource, fields, reqparse, inputs
from flask import jsonify, request, abort
from flask.logging import create_logger
from service.model import Supplier, DataValidationError, Item
from . import status  # HTTP Status Codes
from . import app, api  # Import Flask application

LOG = create_logger(app)
######################################################################
# GET HTML
######################################################################
@app.route("/")
def index():
    """Base URL for our service"""
    return app.send_static_file("index.html")


@app.route("/item")
def items():
    return app.send_static_file("items.html")

############################################################
# Health Endpoint
############################################################
@app.route("/health")
def health():
    """Health Status"""
    return jsonify(dict(status="OK")), status.HTTP_200_OK


# Define the model so that the docs reflect what can be sent
create_model_supplier = api.model('Supplier', {
    'name': fields.String(required=True,
                          description='The name of the Supplier.'),
    'available': fields.Boolean(required=True,
                                description='Is the Supplier available?'),
    'address': fields.String(required=True, description='The address of the Supplier.'),
    'rating': fields.Float(required=True, description='The rating of the Supplier.')
})

supplier_model = api.inherit(
    'SupplierModel',
    create_model_supplier,
    {
        'id': fields.Integer(readOnly=True, description='The unique id assigned internally by service'),
    }
)

create_model_item = api.model('Item', {
    'name': fields.String(required=True,
                          description='The name of the Item.')
})

item_model = api.inherit(
    'ItemModel',
    create_model_item,
    {
        'id': fields.Integer(readOnly=True, description='The unique id assigned internally by service'),
    }
)

supplier_item_relation_model = api.model('Supplier-Item Relation', {
    'supplier_id': fields.Integer(readOnly=True, description='The unique supplier id'),
    'item_id': fields.Integer(readOnly=True, description='The unique item id')
})

supplier_args = reqparse.RequestParser()
supplier_args.add_argument('name', type=str, required=False, help='List Suppliers by name')
supplier_args.add_argument('available', type=inputs.boolean, required=False, help='List Suppliers by availability')
supplier_args.add_argument('address', type=str, required=False, help='List Suppliers by address')
supplier_args.add_argument('rating', type=float, required=False, help='List Suppliers by rating')
supplier_args.add_argument('item-id', type=int, required=False, help='List Suppliers by related Item')


######################################################################
# Function to generate a random API key (good for testing)
######################################################################
def generate_apikey():
    """ Helper function used when generating API keys """
    return secrets.token_hex(16)


######################################################################
#  PATH: /suppliers/<supplier_id>
######################################################################
@api.route('/suppliers/<supplier_id>')
@api.param('supplier_id', 'The Supplier identifier')
class SupplierResource(Resource):
    """
    SupplierResource class

    Allows the manipulation of a single Supplier
    GET /supplier{id} - Returns a Supplier with the id
    PUT /supplier{id} - Update a Supplier with the id
    DELETE /supplier{id} -  Deletes a Supplier with the id
    """
    # -------------------------------------------------------------------
    # RETRIEVE A SUPPLIER
    # -------------------------------------------------------------------
    @api.doc('get_suppliers')
    @api.response(404, 'Supplier not found')
    @api.marshal_with(supplier_model)
    def get(self, supplier_id):
        """
        Retrieve a single Supplier

        This endpoint will return a Supplier based on it's id
        """
        LOG.info("Request for supplier with id: %s", supplier_id)
        supplier = Supplier.find(supplier_id)
        if not supplier:
            abort(status.HTTP_404_NOT_FOUND, f"Supplier with id '{supplier_id}' was not found.")
        return supplier.serialize(), status.HTTP_200_OK

    # -------------------------------------------------------------------
    # UPDATE A SUPPLIER
    # -------------------------------------------------------------------
    @api.doc('update_suppliers', security='apikey')
    @api.response(404, 'Supplier not found')
    @api.response(400, 'The posted Supplier data was not valid')
    @api.expect(supplier_model)
    @api.marshal_with(supplier_model)
    # @token_required
    def put(self, supplier_id):
        """
        Update a Supplier

        This endpoint will update a Supplier based the body that is posted
        """
        LOG.info("Request to update supplier with id: %s", supplier_id)
        supplier = Supplier.find(supplier_id)
        if not supplier:
            abort(status.HTTP_404_NOT_FOUND, f"Supplier with id '{supplier_id}' was not found.")

        LOG.info(f"Payload = {api.payload}")
        supplier.deserialize(api.payload)
        supplier.id = supplier_id
        supplier.update()
        LOG.info("Supplier with ID [%s] updated.", supplier.id)
        return supplier.serialize(), status.HTTP_200_OK

    # -------------------------------------------------------------------
    # DELETE A SUPPLIER
    # -------------------------------------------------------------------
    @api.doc('delete_suppliers', security='apikey')
    @api.response(204, 'Supplier deleted')
    # @token_required
    def delete(self, supplier_id):
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

# #####################################################################
#  PATH: /suppliers
# #####################################################################
@api.route('/suppliers', strict_slashes=False)
class SupplierCollection(Resource):
    """ Handles all interactions with collections of Suppliers """
    # -------------------------------------------------------------------
    # LIST ALL SUPPLIERS
    # -------------------------------------------------------------------
    @api.doc('list_suppliers')
    @api.expect(supplier_args, validate=True)
    @api.marshal_list_with(supplier_model)
    def get(self):
        """Returns all of the Suppliers"""
        LOG.info("Request for supplier list")
        log = ''
        suppliers = []

        args = supplier_args.parse_args(strict=False)
        LOG.info("Arguments parsed.")

        if args['item-id']:
            suppliers = Item.list_suppliers_of_item(args['item-id'])
            log = f" by item_id={args['item-id']}"
        elif args['name']:
            suppliers = Supplier.find_by_name(args['name'])
            log = f" by name={args['name']}"
        elif args['address']:
            suppliers = Supplier.find_by_address(args['address'])
            log = f" by address={args['address']}"
        elif args['available']:
            suppliers = Supplier.find_by_availability(args['available'])
            log = f" by availability={args['available']}"
        elif args['rating']:
            suppliers = Supplier.find_by_rating(args['rating'])
            log = f" by rating>={args['rating']}"
        else:
            suppliers = Supplier.all()

        results = [supplier.serialize() for supplier in suppliers]
        LOG.info(f"Returning {len(results)} suppliers" + log)
        return results, status.HTTP_200_OK

    # -------------------------------------------------------------------
    # ADD A NEW SUPPLIER
    # -------------------------------------------------------------------
    @api.doc('create_suppliers', security='apikey')
    @api.response(400, 'The posted data was not valid')
    @api.expect(create_model_supplier)
    @api.marshal_with(supplier_model, code=201)
    # @token_required
    def post(self):
        """
        Creates a Supplier
        This endpoint will create a Supplier based the data in the body that is posted
        """
        LOG.info("Request to create a supplier")
        check_content_type("application/json")
        supplier = Supplier()
        LOG.info(f"Payload = {api.payload}")
        supplier.deserialize(api.payload)
        supplier.create()
        location_url = api.url_for(SupplierResource, supplier_id=supplier.id, _external=True)
        LOG.info("Supplier with ID [%s] created.", supplier.id)
        return supplier.serialize(), status.HTTP_201_CREATED, {"Location": location_url}

# #####################################################################
# PATH: /suppliers/rating
# #####################################################################
@api.route("/suppliers/rating", strict_slashes=False)
class RateSuppliers(Resource):
    """Action Rating: List all suppliers in descending order of their rating."""
    # -------------------------------------------------------------------
    # SORT SUPPLIERS BY THEIR RATING
    # -------------------------------------------------------------------
    @api.doc('rating_suppliers')
    @api.marshal_with(supplier_model)
    def get(self):
        """Returns all of the Suppliers sorted by their rating."""
        LOG.info("Request for supplier list sort by rating")
        suppliers = []
        suppliers = Supplier.all()
        results = [supplier.serialize() for supplier in suppliers]
        sorted_res = sorted(results, key=lambda d: d["rating"], reverse=True)
        LOG.info("Returning %d suppliers", len(results))
        return sorted_res, status.HTTP_200_OK

# #####################################################################
# PATH: /suppliers/<supplier_id>/active
# #####################################################################
@api.route("/suppliers/<supplier_id>/active")
@api.param('supplier_id', 'The Supplier identifier')
class ActivateSuppliers(Resource):
    """Action Activate: Change the availability status of Supplier to True."""
    @api.doc('activate_suppliers')
    @api.response(404, 'Supplier not found')
    @api.response(400, 'Supplier is already active')
    @api.marshal_with(supplier_model)
    def put(self, supplier_id):
        """
        Activate a Supplier
        This endpoint will update a Supplier based the body that is posted
        """
        LOG.info("Request to activate supplier with id: %s", supplier_id)

        supplier = Supplier.find(supplier_id)

        if not supplier:
            abort(status.HTTP_404_NOT_FOUND, f"Supplier with id '{supplier_id}' was not found.")

        if supplier.available:
            abort(status.HTTP_400_BAD_REQUEST, f"Supplier with id '{supplier_id}' is already active.")

        supplier.available = True
        supplier.id = supplier_id
        supplier.update()

        LOG.info("Supplier with ID [%s] activated", supplier.id)
        return supplier.serialize(), status.HTTP_200_OK

# #####################################################################
# PATH: /suppliers/<supplier_id>/active
# #####################################################################
@api.route("/suppliers/<supplier_id>/deactive")
@api.param('supplier_id', 'The Supplier identifier')
class DeactiveSupplier(Resource):
    """Action Deactivate: Change the availability status of Supplier to False."""
    @api.doc('deactivate_suppliers')
    @api.response(404, 'Supplier not found')
    @api.response(400, 'Supplier is already deactive')
    @api.marshal_with(supplier_model)
    def delete(self, supplier_id):
        """
        Deactivate  a Supplier

        This endpoint will update a Supplier based the body that is posted
        """
        LOG.info("Request to deactivate supplier with id: %s", supplier_id)

        supplier = Supplier.find(supplier_id)

        if not supplier:
            abort(status.HTTP_404_NOT_FOUND, f"Supplier with id '{supplier_id}' was not found.")

        if not supplier.available:
            abort(status.HTTP_400_BAD_REQUEST, f"Supplier with id '{supplier_id}' is already deactivated.")

        supplier.available = False
        supplier.id = supplier_id
        supplier.update()

        LOG.info("Supplier with ID [%s] deactivated", supplier.id)
        return supplier.serialize(), status.HTTP_200_OK

# #####################################################################
#  PATH: /items
# #####################################################################
@api.route('/items', strict_slashes=False)
class ItemCollection(Resource):
    """ Handles all interactions with collections of Items """
    # ------------------------------------------------------------------
    # LIST ALL ITEMS
    # ------------------------------------------------------------------
    @api.doc('list_items')
    @api.marshal_list_with(item_model)
    def get(self):
        """Returns all of the Suppliers"""
        LOG.info("Request for item list")
        items = []
        items = Item.all()

        results = [item.serialize() for item in items]
        LOG.info("Returning %d items", len(results))
        return results, status.HTTP_200_OK

    # ------------------------------------------------------------------
    # ADD A NEW ITEM
    # ------------------------------------------------------------------
    @api.doc('create_items', security='apikey')
    @api.response(400, 'The posted data was not valid')
    @api.expect(create_model_item)
    @api.marshal_with(item_model, code=201)
    # @token_required
    def post(self):
        """
        Creates an item
        This endpoint will create an item based the data in the body that is posted
        """
        try:
            LOG.info("Request to create an item")
            check_content_type("application/json")
            item = Item()
            item.deserialize(api.payload)
            item.create()
            message = item.serialize()

            LOG.info("Item with ID [%s] created.", item.id)
        except DataValidationError as error:
            abort(status.HTTP_400_BAD_REQUEST, str(error))
        return message, status.HTTP_201_CREATED

# #####################################################################
#  PATH: /items/{id}
# #####################################################################
@api.route('/items/<item_id>')
@api.param('item_id', 'The Item identifier')
class ItemResource(Resource):
    """
    ItemResource class
    Allows the manipulation of a single Pet
    GET /pet{id} - Returns a Pet with the id
    DELETE /pet{id} -  Deletes a Pet with the id
    """
    # ------------------------------------------------------------------
    # RETRIEVE A PET
    # ------------------------------------------------------------------
    @api.doc('get_item')
    @api.response(404, 'Item not found')
    @api.marshal_with(item_model)
    def get(self, item_id):
        """
        Retrieve a single Item
        This endpoint will return a Pet based on it's id
        """
        LOG.info("Request to Retrieve a item with id [%s]", item_id)
        item = Item.find(item_id)
        if not item:
            abort(status.HTTP_404_NOT_FOUND, f"Item with id '{item_id}' was not found.")
        return item.serialize(), status.HTTP_200_OK

    # ------------------------------------------------------------------
    # DELETE AN ITEM
    # ------------------------------------------------------------------
    @api.doc('delete_items', security='apikey')
    @api.response(204, 'Item deleted')
    # @token_required
    def delete(self, item_id):
        """
        Delete an Item

        This endpoint will delete an Item based the id specified in the path
        """
        LOG.info("Request to delete item with id: %s", item_id)
        item = Item.find_by_id(item_id)
        if item:
            item.delete()

        LOG.info("Item with ID [%s] delete complete.", item_id)
        return "", status.HTTP_204_NO_CONTENT

# #####################################################################
#  PATH: /suppliers/{sid}}/items/{iid}
# #####################################################################
@api.route('/suppliers/<supplier_id>/items/<item_id>')
@api.param('supplier_id', 'The Supplier identifier')
@api.param('item_id', 'The Item identifier')
class SupplierItemRelation(Resource):
    """
    SupplierItemRelation class
    Allows the manipulation of a Supplier-Item Relation

    POST /suppliers/<supplier_id>/items/<item_id> - Create a Supplier-Item Relation
    DELETE /suppliers/<supplier_id>/items/<item_id> -  Deletes a Supplier-Item Relation
    """
    # ------------------------------------------------------------------
    # ADD AN ITEM TO A SUPPLIER
    # ------------------------------------------------------------------
    @api.doc('add_supplier_item_relation')
    @api.response(404, 'Supplier or Item not found')
    @api.marshal_with(supplier_item_relation_model)
    def post(self, supplier_id: int, item_id: int):
        """
        Add an item to a Supplier

        The endpoint will add an item to a supplier in the relationship table
        """
        LOG.info("Request to add an item to a supplier with id: %s", supplier_id)
        # item_id = request.args.get("item-id")
        item = Item.find_by_id(item_id)
        if not item:
            abort(status.HTTP_404_NOT_FOUND, f"Item with id '{item_id}' was not found.")
        Supplier.create_item_for_supplier(supplier_id=supplier_id, item=item)
        message = {"supplier_id": supplier_id, "item_id": item_id}

        LOG.info("Successfully add an item %s to supplier %s", item_id, supplier_id)
        return message, status.HTTP_201_CREATED

    # ------------------------------------------------------------------
    # DELETE AN SUPPLIER
    # ------------------------------------------------------------------
    @api.doc('delete_supplier_item_relation', security='apikey')
    @api.response(204, 'Supplier-Item relation deleted')
    # @token_required
    def delete(self, supplier_id: int, item_id: int):
        """
        Delete an item of a Supplier
        """
        LOG.info("Delete an item of supplier %s", supplier_id)
        item = Item.find_by_id(item_id)
        if item:
            Supplier.delete_item_for_supplier(supplier_id, item)

        LOG.info("Item with ID [%s] delete for supplier %s complete.", item_id, supplier_id)
        return "", status.HTTP_204_NO_CONTENT

######################################################################
#  PATH: /suppliers/{sid}}/items
######################################################################
@api.route('/suppliers/<supplier_id>/items', strict_slashes=False)
@api.param('supplier_id', 'The Supplier identifier')
class SupplierItemRelationCollection(Resource):
    """ Handles interactions with collections of Items of some supplier """
    # ------------------------------------------------------------------
    # LIST ALL ITEMS OF A SUPPLIER
    # ------------------------------------------------------------------
    @api.doc('list_items_of_supplier')
    @api.response(404, 'Supplier not found')
    @api.marshal_list_with(item_model)
    def get(self, supplier_id):
        """ Returns all of the Items of a Supplier """
        LOG.info("List all items of supplier %s", supplier_id)
        items = []
        items = Supplier.list_items_of_supplier(supplier_id)

        results = [item.serialize() for item in items]
        LOG.info("Returning %d items", len(results))
        return results, status.HTTP_200_OK


######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################
# def abort(error_code: int, message: str):
#     """Logs errors before aborting"""
#     LOG.info(message)
#     api.abort(error_code, message)

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
