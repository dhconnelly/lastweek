from flask import jsonify
from werkzeug.wrappers import Response


def unauthorized(message: str = None) -> Response:
    json = {"error": "unauthorized"}
    if message is not None:
        json["message"] = message
    response = jsonify(json)
    response.status_code = 401
    return response