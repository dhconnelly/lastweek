from flask import render_template, Response

from app.main import main


@main.app_errorhandler(404)
def page_not_found(_) -> Response:
    """Handles HTTP 404 errors"""
    return render_template("404.html.j2"), 404


@main.app_errorhandler(500)
def internal_server_error(_) -> Response:
    """Handles HTTP 500 errors"""
    return render_template("500.html.j2"), 500