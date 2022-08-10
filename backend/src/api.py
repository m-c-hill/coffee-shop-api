import json

from flask import Flask, abort, jsonify, request
from flask_cors import CORS

from .auth.auth import AuthError, requires_auth
from .database.models import Drink, db_drop_and_create_all, setup_db

# =============
#  API Config
# =============

app = Flask(__name__)
setup_db(app)
db_drop_and_create_all()  # Uncomment to reset the local sqlite database
CORS(app)


# ============
#  Endpoints
# ============


@app.route("/drinks")
def drinks():
    """
    Return limited information for all drinks currently on the menu
    """
    drinks = Drink.query.all()
    if len(drinks) == 0:
        abort(404)

    return (
        jsonify({"success": True, "drinks": [drink.short() for drink in drinks]}),
        200,
    )


@app.route("/drinks-detail")
@requires_auth("get:drinks-detail")
def drinks_detailed(jwt):
    """
    Return full information for all drinks currently on the menu
    """
    drinks = Drink.query.all()
    if len(drinks) == 0:
        abort(404)

    return jsonify({"success": True, "drinks": [drink.long() for drink in drinks]}), 200


@app.route("/drinks", methods=["POST"])
@requires_auth("post:drinks")
def create_drink(jwt):
    """
    Add a new drink to the menu
    """
    body = request.get_json()

    new_title = body.get("title")
    new_recipe = json.dumps(body.get("recipe"))

    try:
        new_drink = Drink(title=new_title, recipe=new_recipe)
        new_drink.insert()
    except:
        abort(422)

    return jsonify({"success": True, "drinks": [new_drink.long()]})


@app.route("/drinks/<int:drink_id>", methods=["PATCH"])
@requires_auth("patch:drinks")
def update_drink(jwt, drink_id):
    """
    Add a new drink to the menu
    """
    body = request.get_json()

    try:
        drink = Drink.query.filter(Drink.id == drink_id).one_or_none()
        if drink is None:
            abort(404)

        if body.get("title"):
            drink.title = body.get("title")
        if body.get("recipe"):
            drink.recipe = json.dumps(body.get("recipe"))

        drink.update()

    except:
        abort(422)

    return jsonify({"success": True, "drinks": [drink.long()]})


@app.route("/drinks/<int:drink_id>", methods=["DELETE"])
@requires_auth("delete:drinks")
def delete_drink(jwt, drink_id):
    """
    Add a new drink to the menu
    """
    drink = Drink.query.filter(Drink.id == drink_id).one_or_none()
    if drink is None:
        abort(404)

    try:
        drink.delete()
    except:
        abort(422)

    return jsonify({"success": True, "delete": drink_id})


# =================
#  Error Handling
# =================


@app.errorhandler(400)
def resource_not_found(error):
    return jsonify({"success": False, "error": 400, "message": "bad request"}), 400


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


@app.errorhandler(AuthError)
def unauthorized(error):
    return (
        jsonify(
            {
                "success": False,
                "error": error.status_code,
                "message": error.error.get("description"),
            }
        ),
        error.status_code,
    )
