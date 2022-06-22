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

from flask import jsonify, request, url_for, abort
from service.model import Supplier
from . import status  # HTTP Status Codes
from . import app  # Import Flask application


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Root URL response"""
    app.logger.info("Request for Root URL")
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
    app.logger.info("Request for supplier list")
    suppliers = []
    name = request.args.get("name")
    if name:
        suppliers = Supplier.find_by_name(name)
    else:
        suppliers = Supplier.all()

    results = [supplier.serialize() for supplier in suppliers]
    app.logger.info("Returning %d suppliers", len(results))
    return jsonify(results), status.HTTP_200_OK


######################################################################
# RETRIEVE A SUPPLIER
######################################################################
@app.route("/pets/<int:pet_id>", methods=["GET"])
def get_pets(pet_id):
    """
    Retrieve a single Pet

    This endpoint will return a Pet based on it's id
    """
    app.logger.info("Request for pet with id: %s", pet_id)
    pet = Pet.find(pet_id)
    if not pet:
        abort(status.HTTP_404_NOT_FOUND, f"Pet with id '{pet_id}' was not found.")

    app.logger.info("Returning pet: %s", pet.name)
    return jsonify(pet.serialize()), status.HTTP_200_OK


######################################################################
# ADD A NEW PET
######################################################################
@app.route("/pets", methods=["POST"])
def create_pets():
    """
    Creates a Pet
    This endpoint will create a Pet based the data in the body that is posted
    """
    app.logger.info("Request to create a pet")
    check_content_type("application/json")
    pet = Pet()
    pet.deserialize(request.get_json())
    pet.create()
    message = pet.serialize()
    location_url = url_for("get_pets", pet_id=pet.id, _external=True)

    app.logger.info("Pet with ID [%s] created.", pet.id)
    return jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}


######################################################################
# UPDATE AN EXISTING PET
######################################################################
@app.route("/pets/<int:pet_id>", methods=["PUT"])
def update_pets(pet_id):
    """
    Update a Pet

    This endpoint will update a Pet based the body that is posted
    """
    app.logger.info("Request to update pet with id: %s", pet_id)
    check_content_type("application/json")

    pet = Pet.find(pet_id)
    if not pet:
        abort(status.HTTP_404_NOT_FOUND, f"Pet with id '{pet_id}' was not found.")

    pet.deserialize(request.get_json())
    pet.id = pet_id
    pet.update()

    app.logger.info("Pet with ID [%s] updated.", pet.id)
    return jsonify(pet.serialize()), status.HTTP_200_OK


######################################################################
# DELETE A PET
######################################################################
@app.route("/pets/<int:pet_id>", methods=["DELETE"])
def delete_pets(pet_id):
    """
    Delete a Pet

    This endpoint will delete a Pet based the id specified in the path
    """
    app.logger.info("Request to delete pet with id: %s", pet_id)
    pet = Pet.find(pet_id)
    if pet:
        pet.delete()

    app.logger.info("Pet with ID [%s] delete complete.", pet_id)
    return "", status.HTTP_204_NO_CONTENT


######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################


def check_content_type(media_type):
    """Checks that the media type is correct"""
    content_type = request.headers.get("Content-Type")
    if content_type and content_type == media_type:
        return
    app.logger.error("Invalid Content-Type: %s", content_type)
    abort(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        "Content-Type must be {}".format(media_type),
    )
