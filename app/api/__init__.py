from flask import Blueprint

api = Blueprint("api", __name__)

from . import authentication, errors, users

# routes:
# /users/<id> (GET) return user metadata
# /users/<id>/weeks/ (GET) get all user snippets
# /users/<id>/weeks/<year>/<week> (GET, POST) get/set specific user week