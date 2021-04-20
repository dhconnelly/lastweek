from flask import Blueprint

api = Blueprint("api", __name__)

from . import authentication, errors, users, weeks

# routes:
# /user (GET) return user metadata
# /weeks/ (GET) get all user snippets
# /weeks/current (GET) get current week
# /weeks/<year>/<week> (GET, POST) get/set specific user week