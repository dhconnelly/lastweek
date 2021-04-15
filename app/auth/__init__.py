from flask import Blueprint

auth = Blueprint("auth", __name__)

# TODO: seems bad
from . import views