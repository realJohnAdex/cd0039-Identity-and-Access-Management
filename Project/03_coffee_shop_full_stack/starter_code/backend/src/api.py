import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth


app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route("/drinks")
def retrieve_all_drinks():
    try:
        drinks_selection = Drink.query.order_by(Drink.id).all()
        if len(drinks_selection) == 0:
            #not found error because no drinks exists in database
            abort(404)
        formatted_drinks = [drink.short() for drink in drinks_selection]

        return jsonify(
            {
                "success": True,
                "drinks": formatted_drinks,
            }
        )
    except:
        abort(400)


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route("/drinks-detail")
@requires_auth('get:drinks-detail')
def retrieve_all_drinks_detail(payload):
    try:
        drinks_selection = Drink.query.order_by(Drink.id).all()
        if len(drinks_selection) == 0:
            #not found error because no drinks exists in database
            abort(404)
        formatted_drinks = [drink.long() for drink in drinks_selection]

        return jsonify(
            {
                "success": True,
                "drinks": formatted_drinks,
            }
        )
    except:
        abort(400)


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route("/drinks", methods=['POST'])
@requires_auth('post:drinks')
def create_new_drink(payload):
    body = request.get_json()

    new_title = body.get("title", None)
    new_recipe = body.get("recipe", None)
    
    try:
        new_drink = Drink(
            title=new_title,
            recipe=new_recipe,
            )
        new_drink.insert()

        return jsonify(
            {
                "success": True,
                "drinks": new_drink,
            }
        )
    except:
        abort(422)

'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route("/drinks/<int:drink_id>", methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(payload, drink_id):
    body = request.get_json()

    new_title = body.get("title", None)
    new_recipe = body.get("recipe", None)
    try:
        drink = Drink.query.filter(Drink.id == drink_id).one_or_none()
        if question is None:
            abort(404)
        drink.title = new_title
        drink.recipe = new_recipe
        drink.update()

        updated_drink = Drink.query.filter(Drink.id == drink_id).one_or_none()

        return jsonify(
            {
                "success": True,
                "drinks": updated_drink.long(),
            }
        )
    except:
        abort(422)

'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route("/drinks/<int:drink_id>", methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, drink_id):
    try:
        drink = Drink.query.filter(Drink.id == drink_id).one_or_none()
        if question is None:
            abort(404)

        drink.delete()

        return jsonify(
            {
                "success": True,
                "deleted": drink_id,
            }
        )
    except:
        abort(422)

# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''
@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False, 
        "error": 400, 
        "message": "bad request"
    }), 400


'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False, 
        "error": 404, 
        "message": "resource not found"
    }),404


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''
@app.errorhandler(AuthError)
def authentication_error(error):
    return jsonify({
        'success': False,
        'error': error.error['code'],
        'message': error.error['description']
    }), error.status_code
