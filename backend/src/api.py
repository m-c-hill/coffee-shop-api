import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

# =============
#  API Config
# =============

app = Flask(__name__)
setup_db(app)
db_drop_and_create_all()
CORS(app)

# ============
#  Endpoints
# ============


@app.route("/drinks")
def drinks():
    """
    Return limited information for all drinks currently on the menu
    """
    selection = Drink.query.all()
    if len(selection) == 0:
        abort(404)
    drinks = [drink.short() for drink in selection]

    return jsonify({"success": True, "drinks": drinks})


# TODO: should require the get:drinks-detail permission
@app.route("/drinks-detail")
def drinks_detailed():
    """
    Return full information for all drinks currently on the menu
    """
    selection = Drink.query.all()
    if len(selection) == 0:
        abort(404)
    drinks = [drink.long() for drink in selection]

    return jsonify({"success": True, "drinks": drinks})


# TODO: should require the post:drinks permission
@app.route("/drinks", methods=["POST"])
def create_drink():
    """
    Add a new drink to the menu
    """

    drink = "NEW DRINK"  # drink.long()
    return jsonify({"success": True, "drinks": drink})


# TODO: should require the patch:drinks permission
@app.route("/drinks", methods=["PATCH"])
def update_drink():
    """
    Add a new drink to the menu
    """

    # should respond with a 404 error if <id> is not found

    drink = "UPDATED DRINK"  # drink.long()
    return jsonify({"success": True, "drinks": drink})


# TODO: should require the patch:drinks permission
@app.route("/drinks/<int:id>", methods=["PATCH"])
def delete_drink(drink_id):
    """
    Add a new drink to the menu
    """

    # should respond with a 404 error if <id> is not found

    return jsonify({"success": True, "delete": drink_id})


# =================
#  Error Handling
# =================

"""
Example error handling for unprocessable entity
"""


@app.errorhandler(400)
def resource_not_found(error):
    return jsonify({"success": False, "error": 400, "message": "bad request"}), 400


@app.errorhandler(401)
def unauthorized(error):
    return jsonify({"success": False, "error": 401, "message": "unauthorized"}), 401


@app.errorhandler(403)
def forbidden(error):
    return (
        jsonify(
            {
                "success": False,
                "error": 403,
                "message": "forbidden - user does not have permission to access this resource",
            }
        ),
        403,
    )


@app.errorhandler(404)
def resource_not_found(error):
    return jsonify({"success": False, "error": 404, "message": "not found"}), 404


@app.errorhandler(422)
def unprocessable(error):
    return (jsonify({"success": False, "error": 422, "message": "unprocessable"}), 422)


@app.errorhandler(500)
def unprocessable(error):
    return (
        jsonify({"success": False, "error": 500, "message": "server side error"}),
        500,
    )
