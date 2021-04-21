from flask import jsonify
from werkzeug.wrappers import Response

from . import api


class ValidationError(ValueError):
    pass


def unauthorized(message: str = None) -> Response:
    json = {"error": "unauthorized"}
    if message:
        json["message"] = message
    response = jsonify(json)
    response.status_code = 401
    return response


def bad_request(message: str = None) -> Response:
    json = {"error": "bad request"}
    if message:
        json["message"] = message
    response = jsonify(json)
    response.status_code = 400
    return response


@api.errorhandler(ValidationError)
def validation_error(e):
    return bad_request(e.args[0])