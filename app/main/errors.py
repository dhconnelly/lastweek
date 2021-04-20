from flask import render_template, Response
from flask.globals import request
from flask.json import jsonify

from app.main import main


@main.app_errorhandler(403)
def forbidden(_) -> Response:
    if (
        request.accept_mimetypes.accept_json
        and not request.accept_mimetypes.accept_html
    ):
        response = jsonify({"error": "forbidden"})
        response.status_code = 403
        return response
    return render_template("403.html.j2"), 403


@main.app_errorhandler(404)
def page_not_found(_) -> Response:
    """Handles HTTP 404 errors"""
    if (
        request.accept_mimetypes.accept_json
        and not request.accept_mimetypes.accept_html
    ):
        response = jsonify({"error": "not found"})
        response.status_code = 404
        return response
    return render_template("404.html.j2"), 404


@main.app_errorhandler(500)
def internal_server_error(_) -> Response:
    """Handles HTTP 500 errors"""
    return render_template("500.html.j2"), 500